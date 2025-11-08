"""Core image processing helpers for USCIS-compliant passport photos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from rembg import remove

USCIS_WIDTH_PX = 600
USCIS_HEIGHT_PX = 600
USCIS_DPI = 300


@dataclass
class CropSuggestion:
    """Describes a suggested crop rectangle."""

    left: int
    top: int
    right: int
    bottom: int

    def to_tuple(self) -> Tuple[int, int, int, int]:
        return (self.left, self.top, self.right, self.bottom)


def load_image(path: Path | str) -> Image.Image:
    """Load an image from disk and convert it to RGB."""

    image = Image.open(path)
    return image.convert("RGB")


def validate_image_size(image: Image.Image) -> None:
    """Validate that the input image meets the minimum size requirements."""

    width, height = image.size
    if width < USCIS_WIDTH_PX or height < USCIS_HEIGHT_PX:
        raise ValueError(
            "Input image must be at least 600x600 pixels. "
            "Please upload a higher-resolution photo."
        )


def suggest_crop(image: Image.Image) -> Optional[CropSuggestion]:
    """Suggest a crop around the detected face using OpenCV Haar cascades."""

    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    classifier = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = classifier.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(150, 150))

    if len(faces) == 0:
        return None

    x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])

    center_x = x + w // 2
    center_y = y + h // 2

    half_size = max(w, h)
    half_size = int(half_size * 1.7 / 2)

    left = max(center_x - half_size, 0)
    top = max(center_y - half_size, 0)
    right = min(center_x + half_size, image.width)
    bottom = min(center_y + half_size, image.height)

    size = min(right - left, bottom - top)
    right = left + size
    bottom = top + size

    if right > image.width:
        shift = right - image.width
        left -= shift
        right -= shift
    if bottom > image.height:
        shift = bottom - image.height
        top -= shift
        bottom -= shift

    left = max(left, 0)
    top = max(top, 0)

    return CropSuggestion(left=left, top=top, right=right, bottom=bottom)


def crop_image(image: Image.Image, crop_box: Tuple[int, int, int, int]) -> Image.Image:
    """Crop the image to the provided bounding box."""

    cropped = image.crop(crop_box)
    width, height = cropped.size
    if width < USCIS_WIDTH_PX or height < USCIS_HEIGHT_PX:
        raise ValueError(
            "Selected crop is smaller than 600x600 pixels. Adjust the crop to avoid upscaling."
        )
    return ImageOps.fit(cropped, (USCIS_WIDTH_PX, USCIS_HEIGHT_PX), method=Image.LANCZOS)


def remove_background(image: Image.Image) -> Image.Image:
    """Remove background from an image and replace it with solid white."""

    rgba = image.convert("RGBA")
    segmented = remove(rgba)
    mask = segmented.split()[-1]

    smooth_mask = mask.filter(ImageFilter.GaussianBlur(radius=1))

    white_bg = Image.new("RGBA", segmented.size, (255, 255, 255, 255))
    white_bg.paste(segmented, mask=smooth_mask)

    return white_bg.convert("RGB")


def prepare_passport_photo(
    image: Image.Image,
    crop_box: Optional[Tuple[int, int, int, int]] = None,
    *,
    auto_crop: bool = False,
) -> Image.Image:
    """Generate a USCIS-compliant passport photo from the provided image."""

    validate_image_size(image)

    working = image.copy()

    if crop_box is not None:
        cropped = crop_image(working, crop_box)
    elif auto_crop:
        suggestion = suggest_crop(working)
        if suggestion:
            cropped = crop_image(working, suggestion.to_tuple())
        else:
            cropped = ImageOps.fit(working, (USCIS_WIDTH_PX, USCIS_HEIGHT_PX), method=Image.LANCZOS)
    else:
        cropped = ImageOps.fit(working, (USCIS_WIDTH_PX, USCIS_HEIGHT_PX), method=Image.LANCZOS)

    processed = remove_background(cropped)

    processed.info["dpi"] = (USCIS_DPI, USCIS_DPI)
    return processed


def save_passport_photo(image: Image.Image, path: Path | str) -> None:
    """Save an image to disk with the correct DPI metadata."""

    image.save(path, format="JPEG", dpi=(USCIS_DPI, USCIS_DPI), quality=95)


__all__ = [
    "CropSuggestion",
    "load_image",
    "validate_image_size",
    "suggest_crop",
    "crop_image",
    "remove_background",
    "prepare_passport_photo",
    "save_passport_photo",
]
