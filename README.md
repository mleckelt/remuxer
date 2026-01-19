# Remuxer

Small Streamlit app to remux audio tracks (DTS -> AC3) while keeping
video and subtitle streams intact.

Usage
- Install dependencies (see below).
- Run with: `streamlit run app.py`.

Notes
- This tool calls external binaries `ffmpeg` and `ffprobe`. Make sure
  they are installed and available on your PATH.
- The repository includes a `pyproject.toml` for project metadata and a
  placeholder `uv.lock`. To generate a real lock file and create the
  environment, install `uv` and run the appropriate `uv` commands (see
  `uv` documentation). If you prefer not to use `uv`, you can create a
  virtual environment and `pip install -r requirements.txt`.

Dependencies
- streamlit

Security & Privacy
- This repository contains no personal information. Example paths in the
  UI have been sanitized to generic placeholders.

Contact
- If you want further changes (real `uv.lock` generation or CI setup),
  tell me and I can try to run `uv` here (requires `uv` installed).

