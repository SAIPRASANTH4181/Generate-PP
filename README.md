# Passport Photo Generator

An end-to-end Python project for generating passport photos for multiple international standards from any high-resolution portrait. The project ships with a Streamlit web UI and a CLI for batch processing.

## Features

- **Image upload & preview** – Upload JPEG/PNG images and review the source photo before editing.
- **Multiple passport formats** – Generate photos for the United States, India, the United Kingdom, and easily extend the standards catalogue.
- **Interactive crop** – Drag-and-adjust crop constrained to the exact aspect ratio required by the selected passport format. Optional face detection automatically centers the crop.
- **Automated background cleanup** – Foreground segmentation (powered by [rembg](https://github.com/danielgatis/rembg)) removes busy backgrounds and replaces them with a smooth white fill.
- **Strict size validation** – Images smaller than the target resolution are rejected; the tool never upscales undersized inputs.
- **One-click export** – Save the processed JPEG with the correct DPI metadata. Optionally export a printable sheet with multiple copies sized for the chosen standard.
- **CLI support** – Batch-process multiple files, with optional face-detection cropping, sheet generation, and standard selection.

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

Use the sidebar to choose the passport format you need. Crop constraints, face-detection assistance, downloads, and printable sheets update automatically to match the selected standard.

### UI Workflow

1. Upload a high-resolution portrait (ensure it meets the minimum pixel dimensions for your selected standard).
2. (Optional) Enable face detection to auto-center the crop, then fine-tune manually.
3. Click **Process Image** to generate the passport photo.
4. Download the cleaned passport image, and optionally the printable sheet preview.

## Command Line Interface

Run the CLI via the module entry point:

```bash
python -m passport_photo /path/to/input.jpg --auto-crop --sheet --standard uk --output-dir processed
```

Arguments:

- `inputs`: One or more image paths.
- `--output-dir`: Destination directory (defaults to the current working directory).
- `--auto-crop`: Attempt to auto-center the crop using face detection.
- `--sheet`: Also render a printable sheet containing multiple copies of the processed photo.
- `--standard`: Choose the passport format (`us`, `india`, `uk`). Defaults to `us`.

Each processed image is saved as `<original_stem>_<standard>_passport.jpg` with the correct DPI metadata. If `--sheet` is enabled, a `<original_stem>_<standard>_passport_<sheet_label>.jpg` companion file is produced.

## Project Structure

```
app/
  main.py              # Streamlit UI
passport_photo/
  __init__.py
  __main__.py          # Allows `python -m passport_photo`
  cli.py               # Batch processing CLI
  processing.py        # Core validation, cropping, background removal
  standards.py         # Passport format definitions
  sheet.py             # Printable sheet generation helpers
requirements.txt       # Python dependencies
```

## Testing

A lightweight sanity check to ensure the package imports correctly:

```bash
python -m compileall passport_photo app
```

## License

MIT
