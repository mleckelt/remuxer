"""Simple Streamlit app to remux audio tracks to AC3.

This app provides a minimal UI to remux video files using ffmpeg
while keeping video and subtitle streams untouched. It is intended
as a lightweight helper and does not replace full-featured
transcoding workflows.

Security note: This tool calls external binaries (`ffmpeg`/`ffprobe`).
Ensure those tools are installed and that input paths are trusted.
"""

import subprocess
import streamlit as st
import re
import os

st.set_page_config(page_title="Remux DTS to AC3", layout="centered")
st.title("Remux Video: DTS ➡ AC3")


def get_video_duration(input_filename):
    """Return the duration (in seconds) of a media file using ffprobe.

    Returns None on error and shows an error in the Streamlit UI.
    """
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                input_filename,
            ],
            capture_output=True,
            text=True,
        )

        # ffprobe returns only the duration on success
        return float(result.stdout.strip())
    except Exception as e:
        st.error(f"Failed to parse duration: {e}")
        return None


def time_str_to_seconds(time_str):
    """Convert a timestamp like '00:01:23.45' to seconds as float."""
    h, m, s = time_str.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def convert_to_ac3(input_filename: str, output_path: str):
    """Remux the input file to an output path with AC3 audio.

    The function keeps video and subtitle streams intact and only
    remuxes/re-encodes audio to AC3 at 640 kbps.
    """
    # Strip leading/trailing whitespace and quotes
    input_filename = os.path.expanduser(input_filename.strip().strip('"').strip("'"))
    input_filename = os.path.normpath(input_filename)
    output_path = os.path.expanduser(output_path.strip().strip('"').strip("'"))
    output_path = os.path.normpath(output_path)

    st.text(f"Saving to: {output_path}")

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
        "-i",
        input_filename,
        "-map",
        "0",
        "-c:v",
        "copy",
        "-c:a",
        "ac3",
        "-b:a",
        "640k",
        "-c:s",
        "copy",
        output_path,
    ]

    try:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

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
    """Open a native file picker and return the selected path.

    This uses `tkinter` if available. In headless/container environments
    the picker will not be available and the function returns None.
    """
    try:
        # Import only when needed to avoid GUI imports on servers
        from tkinter import Tk, filedialog  # type: ignore
    except Exception:
        st.warning("Native file picker not available in this environment.")
        return None

    if st.button(label):
        root = Tk()
        root.withdraw()  # Hide tkinter window
        path = filedialog.askopenfilename()
        root.destroy()
        return path
    return None


# --- UI ---
input_file = st.text_input("Step 1: Paste full path to input file or use the picker")
if input_file:
    st.text(f"Selected: {input_file}")
    output_file = st.text_input("Step 2: Output file path (e.g., /path/to/output.mkv)")
    if st.button("Convert to AC3"):
        if not output_file:
            st.error("Please specify an output path.")
        else:
            convert_to_ac3(input_file, output_file)
