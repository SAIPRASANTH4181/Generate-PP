"""Utilities for arranging passport photos on printable sheets."""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from PIL import Image

from .standards import DEFAULT_STANDARD, PassportStandard


def _generate_positions(
    canvas_size: Tuple[int, int],
    photo_size: Tuple[int, int],
    copies: int,
    margin_px: int,
) -> List[Tuple[int, int]]:
    """Generate a grid of positions for placing passport photos."""

    canvas_width, canvas_height = canvas_size
    photo_width, photo_height = photo_size

    positions: List[Tuple[int, int]] = []

    if photo_width > canvas_width or photo_height > canvas_height:
        raise ValueError("Passport photo is larger than the configured sheet canvas.")

    y = margin_px
    while y + photo_height <= canvas_height - margin_px and len(positions) < copies:
        x = margin_px
        while x + photo_width <= canvas_width - margin_px and len(positions) < copies:
            positions.append((x, y))
            x += photo_width + margin_px
        y += photo_height + margin_px

    if not positions:
        raise ValueError("Unable to place any passport photos on the sheet with the given configuration.")

    return positions


def create_passport_sheet(
    photo: Image.Image,
    *,
    copies: int | None = None,
    standard: PassportStandard = DEFAULT_STANDARD,
) -> Image.Image:
    """Create a printable sheet containing multiple passport photos."""

    if photo.size != standard.size:
        raise ValueError(
            "Passport photo must match the selected standard before creating a sheet. "
            f"Expected {standard.size}, got {photo.size}."
        )

    sheet_cfg = standard.sheet
    target_copies = copies or sheet_cfg.default_copies

    canvas = Image.new("RGB", sheet_cfg.canvas_size, color=(255, 255, 255))
    positions = _generate_positions(sheet_cfg.canvas_size, photo.size, target_copies, sheet_cfg.margin_px)

    for index in range(min(target_copies, len(positions))):
        x, y = positions[index]
        canvas.paste(photo, (x, y))

    canvas.info["dpi"] = (standard.dpi, standard.dpi)
    return canvas


def save_sheet(
    image: Image.Image,
    path: Path | str,
    *,
    standard: PassportStandard = DEFAULT_STANDARD,
) -> None:
    """Persist the generated sheet with DPI metadata."""

    image.save(path, format="JPEG", dpi=(standard.dpi, standard.dpi), quality=95)


__all__ = ["create_passport_sheet", "save_sheet"]
