"""Save and load .iproj project files.

A .iproj file is a ZIP archive containing:
  project.json  — pipeline structure and step configs
  source.png    — the original source image (lossless PNG)
"""
import json
import os
import warnings
import zipfile

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor

PROJECT_VERSION = 1

# ── Exceptions & warnings ─────────────────────────────────────────────────────


class ProjectFormatError(Exception):
    pass


class ProjectVersionError(Exception):
    pass


class LUTFileNotFoundWarning(UserWarning):
    pass


class UnknownProcessorWarning(UserWarning):
    pass


# ── Tuple fields that must be coerced list→tuple on load ─────────────────────

_TUPLE_FIELDS: dict[str, set[str]] = {
    "HoughLinesTransformation": {"line_color_bgr"},
}


# ── Public API ────────────────────────────────────────────────────────────────


def save_project(path: str, steps: list, original: np.ndarray) -> None:
    """Write pipeline + image to a .iproj ZIP file.

    Args:
        path:     Destination file path (should end in .iproj).
        steps:    list[PipelineStep] from ProcessingPipeline.steps.
        original: The source image as a BGR ndarray.

    Raises:
        OSError: If encoding or writing fails.
    """
    doc = {
        "version": PROJECT_VERSION,
        "steps": _serialize_steps(steps),
    }
    json_bytes = json.dumps(doc, indent=2, ensure_ascii=False).encode("utf-8")

    ok, buf = cv2.imencode(".png", original)
    if not ok:
        raise OSError("Failed to encode source image as PNG")
    img_bytes = buf.tobytes()

    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("project.json", json_bytes)
        zf.writestr("source.png", img_bytes)


def load_project(
    path: str,
) -> tuple[list[tuple[str, BaseProcessor, bool]], np.ndarray]:
    """Load a .iproj file and return (steps, original_image).

    Args:
        path: Path to the .iproj file.

    Returns:
        A tuple of:
          - list of (name, processor, enabled) tuples
          - original image as BGR ndarray

    Raises:
        ProjectFormatError:  Not a valid ZIP or required files missing.
        ProjectVersionError: Unknown or unsupported version field.

    Warns:
        UnknownProcessorWarning: Unrecognised processor type (step skipped).
        LUTFileNotFoundWarning:  cube_path not found on this machine.
    """
    try:
        zf = zipfile.ZipFile(path, "r")
    except (zipfile.BadZipFile, OSError) as exc:
        raise ProjectFormatError(f"Cannot open project file: {exc}") from exc

    with zf:
        names = zf.namelist()
        if "project.json" not in names:
            raise ProjectFormatError("Archive is missing project.json")
        if "source.png" not in names:
            raise ProjectFormatError("Archive is missing source.png")

        try:
            doc = json.loads(zf.read("project.json").decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise ProjectFormatError(f"Corrupted project.json: {exc}") from exc

        version = doc.get("version")
        if version is None:
            raise ProjectVersionError("project.json has no 'version' field")
        if version != PROJECT_VERSION:
            raise ProjectVersionError(
                f"Unsupported project version {version!r} (expected {PROJECT_VERSION})"
            )

        img_array = np.frombuffer(zf.read("source.png"), dtype=np.uint8)
        original = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        if original is None:
            raise ProjectFormatError("source.png could not be decoded as an image")

        step_tuples = _deserialize_steps(doc.get("steps", []))

    return step_tuples, original


# ── Helpers ───────────────────────────────────────────────────────────────────


def _serialize_steps(steps: list) -> list[dict]:
    result = []
    for step in steps:
        config_dict = {
            k: v
            for k, v in vars(step.processor._config).items()
            if not k.startswith("_")
        }
        result.append({
            "name": step.name,
            "type": type(step.processor).__name__,
            "enabled": step.enabled,
            "config": config_dict,
        })
    return result


def _deserialize_steps(
    data: list[dict],
) -> list[tuple[str, BaseProcessor, bool]]:
    registry = _build_registry()
    result = []
    for entry in data:
        type_name = entry.get("type", "")
        if type_name not in registry:
            warnings.warn(
                f"Unknown processor type {type_name!r} — step skipped",
                UnknownProcessorWarning,
                stacklevel=4,
            )
            continue

        config = _coerce_config(type_name, dict(entry.get("config", {})))

        if type_name == "LUT3DTransformation":
            cube_path = config.get("cube_path", "")
            if cube_path and not os.path.isfile(cube_path):
                warnings.warn(
                    f"LUT file not found: {cube_path!r} — step will pass through unchanged",
                    LUTFileNotFoundWarning,
                    stacklevel=4,
                )
                config["cube_path"] = ""

        cls = registry[type_name]
        try:
            processor = cls(**config)
        except Exception as exc:
            warnings.warn(
                f"Could not reconstruct {type_name} from saved config: {exc} — step skipped",
                UnknownProcessorWarning,
                stacklevel=4,
            )
            continue

        result.append((entry["name"], processor, bool(entry.get("enabled", True))))
    return result


def _coerce_config(type_name: str, config: dict) -> dict:
    for field in _TUPLE_FIELDS.get(type_name, set()):
        if field in config and isinstance(config[field], list):
            config[field] = tuple(config[field])
    return config


def _build_registry() -> dict[str, type]:
    from src.processors.color_transformations.gamma import GammaTransformation
    from src.processors.color_transformations.brightness_contrast import BrightnessContrastTransformation
    from src.processors.color_transformations.saturation import SaturationTransformation
    from src.processors.color_transformations.hsv_adjust import HSVAdjustTransformation
    from src.processors.color_transformations.white_balance import WhiteBalanceTransformation
    from src.processors.color_transformations.grayscale import GrayscaleTransformation
    from src.processors.filters.blur import BlurTransformation
    from src.processors.filters.sharpen import SharpenTransformation
    from src.processors.filters.sobel import SobelTransformation
    from src.processors.filters.edge_detect import EdgeDetectTransformation
    from src.processors.filters.threshold import ThresholdTransformation
    from src.processors.filters.hough_lines import HoughLinesTransformation
    from src.processors.filters.morphology import MorphologyTransformation
    from src.processors.filters.skeleton import SkeletonTransformation
    from src.processors.spatial.resize import ResizeTransformation
    from src.processors.spatial.crop import CropTransformation
    from src.processors.spatial.rotate import RotateTransformation
    from src.processors.spatial.flip import FlipTransformation
    from src.processors.tone.exposure import ExposureTransformation
    from src.processors.lut.lut_3d import LUT3DTransformation

    classes = [
        GammaTransformation, BrightnessContrastTransformation,
        SaturationTransformation, HSVAdjustTransformation,
        WhiteBalanceTransformation, GrayscaleTransformation,
        BlurTransformation, SharpenTransformation,
        SobelTransformation, EdgeDetectTransformation,
        ThresholdTransformation, HoughLinesTransformation,
        MorphologyTransformation, SkeletonTransformation,
        ResizeTransformation, CropTransformation,
        RotateTransformation, FlipTransformation,
        ExposureTransformation, LUT3DTransformation,
    ]
    return {cls.__name__: cls for cls in classes}
