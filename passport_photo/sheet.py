"""Utilities for arranging passport photos on printable sheets."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image

from .processing import USCIS_DPI, USCIS_HEIGHT_PX, USCIS_WIDTH_PX

FOUR_BY_SIX_CANVAS = (1200, 1800)  # 4x6 inches at 300 DPI (portrait orientation)


def create_passport_sheet(photo: Image.Image, *, copies: int = 4) -> Image.Image:
    """Create a printable 4x6 inch sheet containing multiple passport photos."""

    if photo.size != (USCIS_WIDTH_PX, USCIS_HEIGHT_PX):
        raise ValueError("Passport photo must be 600x600 pixels before creating a sheet.")

    canvas = Image.new("RGB", FOUR_BY_SIX_CANVAS, color=(255, 255, 255))

    positions = [
        (0, 300),
        (USCIS_WIDTH_PX, 300),
        (0, 900),
        (USCIS_WIDTH_PX, 900),
    ]

    for index in range(min(copies, len(positions))):
        x, y = positions[index]
        canvas.paste(photo, (x, y))

    canvas.info["dpi"] = (USCIS_DPI, USCIS_DPI)
    return canvas


def save_sheet(image: Image.Image, path: Path | str) -> None:
    """Persist the generated sheet with DPI metadata."""

    image.save(path, format="JPEG", dpi=(USCIS_DPI, USCIS_DPI), quality=95)


__all__ = ["create_passport_sheet", "save_sheet", "FOUR_BY_SIX_CANVAS"]
