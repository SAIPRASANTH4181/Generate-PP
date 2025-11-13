"""Passport photo standard definitions for multiple countries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class PassportSheetConfig:
    """Defines how printable sheets should be composed for a standard."""

    canvas_size: Tuple[int, int] = (1200, 1800)  # 4x6 inches at 300 DPI (portrait)
    margin_px: int = 60
    default_copies: int = 4
    label: str = "4×6 in sheet"


@dataclass(frozen=True)
class PassportStandard:
    """Describes the pixel dimensions and metadata for a passport format."""

    code: str
    display_name: str
    width_px: int
    height_px: int
    dpi: int
    description: str
    face_padding: float = 1.7
    sheet: PassportSheetConfig = PassportSheetConfig()

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width_px, self.height_px)

    @property
    def aspect_ratio(self) -> float:
        return self.width_px / self.height_px

    def formatted_dimensions(self) -> str:
        width_in = self.width_px / self.dpi
        height_in = self.height_px / self.dpi
        return f"{width_in:.2f}×{height_in:.2f} in ({self.width_px}×{self.height_px} px)"


STANDARDS: Dict[str, PassportStandard] = {
    "us": PassportStandard(
        code="us",
        display_name="United States (USCIS)",
        width_px=600,
        height_px=600,
        dpi=300,
        description="2×2 in photo for US passports and visas.",
    ),
    "india": PassportStandard(
        code="india",
        display_name="India",
        width_px=600,
        height_px=600,
        dpi=300,
        description="51×51 mm (2×2 in) photo widely accepted for Indian passport services.",
    ),
    "uk": PassportStandard(
        code="uk",
        display_name="United Kingdom",
        width_px=413,
        height_px=531,
        dpi=300,
        description="35×45 mm photo used for UK passport applications.",
        face_padding=1.9,
    ),
}

DEFAULT_STANDARD_CODE = "us"
DEFAULT_STANDARD = STANDARDS[DEFAULT_STANDARD_CODE]


def get_standard(code: str | None) -> PassportStandard:
    """Retrieve a passport standard by code, falling back to the default."""

    if not code:
        return DEFAULT_STANDARD

    key = code.lower()
    if key not in STANDARDS:
        raise KeyError(f"Unknown passport standard '{code}'. Available: {', '.join(sorted(STANDARDS))}")
    return STANDARDS[key]


__all__ = [
    "PassportStandard",
    "PassportSheetConfig",
    "STANDARDS",
    "DEFAULT_STANDARD",
    "DEFAULT_STANDARD_CODE",
    "get_standard",
]
