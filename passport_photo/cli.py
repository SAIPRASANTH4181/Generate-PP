"""Command line interface for batch passport photo processing."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .processing import load_image, prepare_passport_photo, save_passport_photo
from .sheet import create_passport_sheet, save_sheet


def _process_single(input_path: Path, output_path: Path, *, auto_crop: bool, make_sheet: bool) -> None:
    image = load_image(input_path)
    processed = prepare_passport_photo(image, auto_crop=auto_crop)
    save_passport_photo(processed, output_path)

    if make_sheet:
        sheet = create_passport_sheet(processed)
        sheet_path = output_path.with_name(output_path.stem + "_4x6.jpg")
        save_sheet(sheet, sheet_path)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate USCIS-compliant passport photos.")
    parser.add_argument("inputs", nargs="+", type=Path, help="Input image file(s).")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to store processed images (defaults to current directory).",
    )
    parser.add_argument(
        "--auto-crop",
        action="store_true",
        help="Automatically suggest a crop based on face detection.",
    )
    parser.add_argument(
        "--sheet",
        action="store_true",
        help="Also create a 4x6 sheet with multiple copies of each processed photo.",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for input_path in args.inputs:
        try:
            output_path = args.output_dir / (input_path.stem + "_passport.jpg")
            _process_single(input_path, output_path, auto_crop=args.auto_crop, make_sheet=args.sheet)
            print(f"Saved passport photo to {output_path}")
        except Exception as exc:  # pragma: no cover - CLI feedback path
            print(f"Failed to process {input_path}: {exc}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
