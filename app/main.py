"""Streamlit application for generating passport photos."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Optional
import sys

import streamlit as st
from PIL import Image
from streamlit_cropper import st_cropper

# Ensure the repository root (which contains ``passport_photo``) is importable when the
# app is launched via ``streamlit run app/main.py``.
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:  # pragma: no cover - environment specific safeguard
    sys.path.insert(0, str(REPO_ROOT))

from passport_photo.processing import (  # noqa: E402 - imported after sys.path fix
    prepare_passport_photo,
    suggest_crop,
    validate_image_size,
)
from passport_photo.sheet import create_passport_sheet
from passport_photo.standards import (  # noqa: E402 - imported after sys.path fix
    DEFAULT_STANDARD,
    STANDARDS,
    PassportStandard,
)

st.set_page_config(page_title="Passport Photo Generator", page_icon="📷", layout="wide")


def _image_to_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(buffer, format="JPEG", dpi=image.info.get("dpi", (300, 300)), quality=95)
    buffer.seek(0)
    return buffer.getvalue()


def _select_standard() -> PassportStandard:
    """Render a selector for passport standards and return the chosen option."""

    options = sorted(STANDARDS.values(), key=lambda standard: standard.display_name)
    selected = st.sidebar.selectbox(
        "Passport format",
        options,
        format_func=lambda standard: standard.display_name,
        index=next((i for i, opt in enumerate(options) if opt.code == DEFAULT_STANDARD.code), 0),
    )

    st.sidebar.caption(selected.description)
    st.sidebar.metric("Dimensions", selected.formatted_dimensions())
    st.sidebar.metric("DPI", f"{selected.dpi} dpi")

    return selected


def main() -> None:
    st.title("Passport Photo Builder")
    st.markdown(
        """
        Upload a high-resolution portrait, adjust the crop, and automatically create a
        compliant passport photo with a clean background.
        """
    )

    selected_standard = _select_standard()
    st.info(
        f"Currently generating **{selected_standard.display_name}** photos: "
        f"{selected_standard.formatted_dimensions()} at {selected_standard.dpi} dpi."
    )

    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

    if not uploaded_file:
        st.info("Upload an image to get started.")
        return

    try:
        original_image = Image.open(uploaded_file).convert("RGB")
        validate_image_size(original_image, standard=selected_standard)
    except ValueError as exc:
        st.error(str(exc))
        return

    st.subheader("Preview & Crop")
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        st.image(original_image, caption="Original upload", use_column_width=True)

    crop_tuple: Optional[tuple[int, int, int, int]] = None

    with col2:
        auto_crop_enabled = st.checkbox("Suggest crop using face detection", value=True)

        if auto_crop_enabled:
            suggestion = suggest_crop(original_image, standard=selected_standard)
            if suggestion:
                st.caption(
                    "Face detected. You can fine-tune the crop or press Process to apply the suggested framing automatically."
                )
            else:
                st.warning("Face detection failed; adjust the crop manually.")

        crop_box = st_cropper(
            original_image,
            aspect_ratio=(selected_standard.width_px, selected_standard.height_px),
            return_type="box",
            box_color="#00FF00",
            realtime_update=True,
            key="passport-cropper",
        )

        if crop_box is None:
            st.warning("Adjust the crop area before processing the image.")
        else:
            crop_tuple = (
                int(crop_box["left"]),
                int(crop_box["top"]),
                int(crop_box["left"] + crop_box["width"]),
                int(crop_box["top"] + crop_box["height"]),
            )

        st.caption(
            "Drag the handles to fine-tune the crop. Aspect ratio is locked to "
            f"{selected_standard.width_px}:{selected_standard.height_px}."
        )

    st.subheader("Generate Passport Photo")
    sheet_option = st.checkbox(
        f"Also prepare a {selected_standard.sheet.label} with {selected_standard.sheet.default_copies} copies"
    )

    if st.button("Process Image", type="primary"):
        with st.spinner("Processing..."):
            if crop_tuple is None and not auto_crop_enabled:
                st.error("Select a crop area or enable face-detection assisted cropping before processing.")
                return

            try:
                processed = prepare_passport_photo(
                    original_image,
                    crop_tuple,
                    auto_crop=auto_crop_enabled,
                    standard=selected_standard,
                )
            except ValueError as exc:
                st.error(str(exc))
                return

            processed_bytes = _image_to_bytes(processed)

            st.success("Passport photo ready!")
            st.image(
                processed,
                caption=f"{selected_standard.display_name} photo",
                width=min(320, selected_standard.width_px),
            )

            st.download_button(
                label="Download passport photo (JPEG)",
                data=processed_bytes,
                file_name=f"passport_photo_{selected_standard.code}.jpg",
                mime="image/jpeg",
            )

            if sheet_option:
                sheet = create_passport_sheet(processed, standard=selected_standard)
                sheet_bytes = _image_to_bytes(sheet)
                st.image(sheet, caption=f"{selected_standard.sheet.label} preview", width=400)
                st.download_button(
                    label=f"Download {selected_standard.sheet.label} (JPEG)",
                    data=sheet_bytes,
                    file_name=f"passport_sheet_{selected_standard.code}.jpg",
                    mime="image/jpeg",
                )


def run() -> None:  # pragma: no cover - Streamlit entry point
    main()


if __name__ == "__main__":  # pragma: no cover
    run()
