import subprocess
import streamlit as st
import re
import os

st.set_page_config(page_title="Remux DTS to AC3", layout="centered")
st.title("Remux Video: DTS ➡ AC3")

def get_video_duration(input_filename):
    try:
        result = subprocess.run([
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of",
            "default=noprint_wrappers=1:nokey=1", input_filename
        ], capture_output=True, text=True)

        st.text(f"stdout: {result.stdout.strip()}")
        st.text(f"stderr: {result.stderr.strip()}")

        return float(result.stdout.strip())
    except Exception as e:
        st.error(f"Failed to parse duration: {e}")
        return None

def time_str_to_seconds(time_str):
    h, m, s = time_str.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)

def convert_to_ac3(input_filename: str, output_path: str):
    # Strip leading/trailing whitespace and quotes
    # Normalize paths for macOS / Linux
    input_filename = os.path.expanduser(input_filename.strip().strip('"').strip("'"))
    input_filename = os.path.normpath(input_filename.replace("\\", ""))
    output_path = os.path.expanduser(output_path.strip().strip('"').strip("'"))
    output_path = os.path.normpath(output_path.replace("\\", ""))

    st.text(f"Saving to: {output_path}")
    st.text(f"Reading from: {input_filename}")

    if not os.path.exists(input_filename):
        st.error(f"❌ Input file not found: {input_filename}")
        return

    duration = get_video_duration(input_filename)
    if not duration:
        st.error("Could not determine video duration.")
        return

    progress = st.progress(0)
    st.write("Remuxing in progress...")

    command = [
        "ffmpeg",
        "-i", input_filename,
        "-map", "0",
        "-c:v", "copy",
        "-c:a", "ac3",
        "-b:a", "640k",
        "-c:s", "copy",
        output_path
    ]

    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        time_pattern = re.compile(r"time=(\d+:\d+:\d+\.\d+)")
        last_percent = 0

        for line in process.stdout:
            match = time_pattern.search(line)
            if match:
                current_time = time_str_to_seconds(match.group(1))
                percent = min(int((current_time / duration) * 100), 100)
                if percent > last_percent:
                    progress.progress(percent)
                    last_percent = percent

        process.wait()
        progress.progress(100)
        st.success(f"Remux complete! File saved to: {output_path}")
    except Exception as e:
        st.error(f"Error during remuxing: {e}")

# --- File Picker Integration ---
def pick_file(label="Pick a file"):
    if st.button(label):
        root = Tk()
        root.withdraw()  # Hide tkinter window
        path = filedialog.askopenfilename()
        root.destroy()
        return path
    return None

# --- UI ---
input_file = st.text_input("Step 1: Paste full path to input file")
if input_file:
    st.text(f"Selected: {input_file}")
    output_file = st.text_input("Step 2: Output file path (e.g., /Users/you/output.mkv)")
    if st.button("Convert to AC3"):
        if not output_file:
            st.error("Please specify an output path.")
        else:
            convert_to_ac3(input_file, output_file)