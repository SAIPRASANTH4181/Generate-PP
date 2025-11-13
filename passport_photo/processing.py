"""Core image processing helpers for passport photos."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from rembg import remove

from .standards import DEFAULT_STANDARD, PassportStandard


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


def validate_image_size(image: Image.Image, standard: PassportStandard = DEFAULT_STANDARD) -> None:
    """Validate that the input image meets the minimum size requirements."""

    width, height = image.size
    target_width, target_height = standard.size
    if width < target_width or height < target_height:
        raise ValueError(
            "Input image is too small. "
            f"It must be at least {target_width}x{target_height} pixels for {standard.display_name}."
        )


def suggest_crop(
    image: Image.Image,
    standard: PassportStandard = DEFAULT_STANDARD,
) -> Optional[CropSuggestion]:
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

    ratio = standard.aspect_ratio
    padding = standard.face_padding

    target_height = max(h * padding, (w * padding) / ratio)
    target_width = target_height * ratio

    half_width = target_width / 2
    half_height = target_height / 2

    left = int(round(center_x - half_width))
    top = int(round(center_y - half_height))
    right = int(round(center_x + half_width))
    bottom = int(round(center_y + half_height))

    # Ensure the crop stays inside the image boundaries.
    if left < 0:
        right -= left
        left = 0
    if top < 0:
        bottom -= top
        top = 0

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


def crop_image(
    image: Image.Image,
    crop_box: Tuple[int, int, int, int],
    standard: PassportStandard = DEFAULT_STANDARD,
) -> Image.Image:
    """Crop the image to the provided bounding box."""

    cropped = image.crop(crop_box)
    width, height = cropped.size
    target_width, target_height = standard.size
    if width < target_width or height < target_height:
        raise ValueError(
            "Selected crop is too small. "
            f"Ensure the crop is at least {target_width}x{target_height} pixels for {standard.display_name}."
        )
    return ImageOps.fit(cropped, (target_width, target_height), method=Image.LANCZOS)


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
    standard: PassportStandard = DEFAULT_STANDARD,
) -> Image.Image:
    """Generate a passport photo from the provided image using the given standard."""

    validate_image_size(image, standard=standard)

    working = image.copy()

    if crop_box is not None:
        cropped = crop_image(working, crop_box, standard=standard)
    elif auto_crop:
        suggestion = suggest_crop(working, standard=standard)
        if suggestion:
            cropped = crop_image(working, suggestion.to_tuple(), standard=standard)
        else:
            cropped = ImageOps.fit(working, standard.size, method=Image.LANCZOS)
    else:
        cropped = ImageOps.fit(working, standard.size, method=Image.LANCZOS)

    processed = remove_background(cropped)

    processed.info["dpi"] = (standard.dpi, standard.dpi)
    return processed


def save_passport_photo(
    image: Image.Image,
    path: Path | str,
    *,
    standard: PassportStandard = DEFAULT_STANDARD,
) -> None:
    """Save an image to disk with the correct DPI metadata."""

    image.save(path, format="JPEG", dpi=(standard.dpi, standard.dpi), quality=95)


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
