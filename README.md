# USCIS Passport Photo Generator

An end-to-end Python project for generating USCIS-compliant passport photos from any high-resolution portrait. The project ships with a Streamlit web UI and a CLI for batch processing.

## Features

- **Image upload & preview** – Upload JPEG/PNG images and review the source photo before editing.
- **Interactive crop** – Drag-and-adjust crop constrained to the required 1:1 aspect ratio. Optional face detection automatically centers the crop.
- **Automated background cleanup** – Foreground segmentation (powered by [rembg](https://github.com/danielgatis/rembg)) removes busy backgrounds and replaces them with a smooth white fill.
- **Strict size validation** – Images smaller than 600×600 px are rejected; the tool never upscales undersized inputs.
- **One-click export** – Save the processed 2×2 in (600×600 px) JPEG with 300 DPI metadata. Optionally export a printable 4×6 sheet containing four copies.
- **CLI support** – Batch-process multiple files, with optional face-detection cropping and sheet generation.

## Requirements

- Python 3.9+
- System packages required by OpenCV and rembg (e.g., `libgl1`, `libglib2.0-0` on Debian/Ubuntu)

Install Python dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Streamlit Application

```bash
streamlit run app/main.py
```

### UI Workflow

1. Upload a high-resolution portrait (minimum 600×600 px).
2. (Optional) Enable face detection to auto-center the crop, then fine-tune manually.
3. Click **Process Image** to generate the passport photo.
4. Download the cleaned 2×2 image, and optionally the printable 4×6 sheet.

## Command Line Interface

Run the CLI via the module entry point:

```bash
python -m passport_photo /path/to/input.jpg --auto-crop --sheet --output-dir processed
```

Arguments:

- `inputs`: One or more image paths.
- `--output-dir`: Destination directory (defaults to the current working directory).
- `--auto-crop`: Attempt to auto-center the crop using face detection.
- `--sheet`: Also render a 4×6 in sheet containing four copies of the processed photo.

Each processed image is saved as `<original_stem>_passport.jpg` with 300 DPI metadata; if `--sheet` is enabled, a `<original_stem>_passport_4x6.jpg` companion file is produced.

## Project Structure

```
app/
  main.py              # Streamlit UI
passport_photo/
  __init__.py
  __main__.py          # Allows `python -m passport_photo`
  cli.py               # Batch processing CLI
  processing.py        # Core validation, cropping, background removal
  sheet.py             # 4×6 sheet generation helpers
requirements.txt       # Python dependencies
```

## Testing

A lightweight sanity check to ensure the package imports correctly:

```bash
python -m compileall passport_photo app
```

## License

MIT
