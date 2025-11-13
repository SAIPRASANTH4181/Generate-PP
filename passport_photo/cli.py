"""Command line interface for batch passport photo processing."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from .processing import load_image, prepare_passport_photo, save_passport_photo
from .sheet import create_passport_sheet, save_sheet
from .standards import DEFAULT_STANDARD, STANDARDS, get_standard


def _process_single(
    input_path: Path,
    output_path: Path,
    *,
    auto_crop: bool,
    make_sheet: bool,
    standard_code: str,
) -> None:
    image = load_image(input_path)
    standard = get_standard(standard_code)
    processed = prepare_passport_photo(image, auto_crop=auto_crop, standard=standard)
    save_passport_photo(processed, output_path, standard=standard)

    if make_sheet:
        sheet = create_passport_sheet(processed, standard=standard)
        sheet_suffix = standard.sheet.label.replace(" ", "_").replace("×", "x")
        sheet_path = output_path.with_name(output_path.stem + f"_{sheet_suffix}.jpg")
        save_sheet(sheet, sheet_path, standard=standard)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate passport photos for multiple standards.")
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
        help="Also create a printable sheet with multiple copies sized for the selected standard.",
    )
    parser.add_argument(
        "--standard",
        choices=sorted(STANDARDS.keys()),
        default=DEFAULT_STANDARD.code,
        help="Passport standard to apply (defaults to %(default)s).",
    )
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    for input_path in args.inputs:
        try:
            standard = get_standard(args.standard)
            output_path = args.output_dir / (input_path.stem + f"_{standard.code}_passport.jpg")
            _process_single(
                input_path,
                output_path,
                auto_crop=args.auto_crop,
                make_sheet=args.sheet,
                standard_code=args.standard,
            )
            print(f"Saved {standard.display_name} passport photo to {output_path}")
        except Exception as exc:  # pragma: no cover - CLI feedback path
            print(f"Failed to process {input_path}: {exc}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
