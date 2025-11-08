"""Streamlit application for generating USCIS-compliant passport photos."""

from __future__ import annotations

from io import BytesIO
from typing import Optional

import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

from passport_photo.processing import (
    CropSuggestion,
    prepare_passport_photo,
    suggest_crop,
    validate_image_size,
)
from passport_photo.sheet import create_passport_sheet

st.set_page_config(page_title="US Passport Photo Generator", page_icon="📷", layout="wide")


def _relative_rect(suggestion: CropSuggestion, image: Image.Image) -> tuple[float, float, float, float]:
    return (
        suggestion.left / image.width,
        suggestion.top / image.height,
        suggestion.right / image.width,
        suggestion.bottom / image.height,
    )


def _image_to_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="JPEG", dpi=image.info.get("dpi", (300, 300)), quality=95)
    buffer.seek(0)
    return buffer.getvalue()


def main() -> None:
    st.title("USCIS Passport Photo Builder")
    st.markdown(
        """
        Upload a high-resolution portrait, adjust the crop, and automatically create a
        compliant 2x2 inch (600x600 pixel) passport photo with a clean white background.
        """
    )

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if not uploaded_file:
        st.info("Upload an image to get started.")
        return

    try:
        original_image = Image.open(uploaded_file).convert("RGB")
        validate_image_size(original_image)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.subheader("Preview & Crop")
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.image(original_image, caption="Original upload", use_column_width=True)

    with col2:
        auto_crop_enabled = st.checkbox("Suggest crop using face detection", value=True)

        default_rect: Optional[tuple[float, float, float, float]] = None
        if auto_crop_enabled:
            suggestion = suggest_crop(original_image)
            if suggestion:
                default_rect = _relative_rect(suggestion, original_image)
            else:
                st.warning("Face detection failed; adjust the crop manually.")

        crop_box = st_cropper(
            original_image,
            aspect_ratio=(1, 1),
            return_type="box",
            box_color="#00FF00",
            realtime_update=True,
            key="passport-cropper",
            default_rect=default_rect,
        )

        crop_tuple = (
            int(crop_box["left"]),
            int(crop_box["top"]),
            int(crop_box["left"] + crop_box["width"]),
            int(crop_box["top"] + crop_box["height"]),
        )

        st.caption("Drag the handles to fine-tune the crop. Aspect ratio is locked to 1:1.")

    st.subheader("Generate Passport Photo")
    sheet_option = st.checkbox("Also prepare a 4x6 sheet with 4 copies")

    if st.button("Process Image", type="primary"):
        with st.spinner("Processing..."):
            try:
                processed = prepare_passport_photo(original_image, crop_tuple)
            except ValueError as exc:
                st.error(str(exc))
                return

            processed_bytes = _image_to_bytes(processed)

            st.success("Passport photo ready!")
            st.image(processed, caption="USCIS-ready 2x2 photo", width=300)

            st.download_button(
                label="Download passport photo (JPEG)",
                data=processed_bytes,
                file_name="passport_photo.jpg",
                mime="image/jpeg",
            )

            if sheet_option:
                sheet = create_passport_sheet(processed)
                sheet_bytes = _image_to_bytes(sheet)
                st.image(sheet, caption="4x6 sheet preview", width=400)
                st.download_button(
                    label="Download 4x6 sheet (JPEG)",
                    data=sheet_bytes,
                    file_name="passport_sheet_4x6.jpg",
                    mime="image/jpeg",
                )


def run() -> None:  # pragma: no cover - Streamlit entry point
    main()


if __name__ == "__main__":  # pragma: no cover
    run()
