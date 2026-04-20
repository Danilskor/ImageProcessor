from typing import override

import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig
from src.base import InvalidLUTFileError
from .cube_parser import CubeData, CubeFileParser


class LUT3DConfig(BaseProcessorConfig):
    def __init__(self, cube_path: str = "", strength: float = 1.0):
        if not (0.0 <= strength <= 1.0):
            raise ValueError("strength must be in [0.0, 1.0]")
        self.cube_path = cube_path
        self.strength = strength
        self._cube_data: CubeData | None = None
        if cube_path:
            self._cube_data = CubeFileParser.parse(cube_path)

    def update(self, **kwargs) -> None:
        super().update(**kwargs)
        if "cube_path" in kwargs and self.cube_path:
            self._cube_data = CubeFileParser.parse(self.cube_path)


class LUT3DTransformation(BaseProcessor):
    def __init__(self, cube_path: str = "", strength: float = 1.0):
        super().__init__()
        self._config = LUT3DConfig(cube_path, strength)

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        if self._config._cube_data is None:
            return image

        original = image.astype(np.float32) / 255.0
        lut_result = _apply_3d_lut(original, self._config._cube_data)

        strength = self._config.strength
        blended = (1.0 - strength) * original + strength * lut_result
        return np.clip(blended * 255.0, 0, 255).astype(np.uint8)


def _apply_3d_lut(image: np.ndarray, lut_data: CubeData) -> np.ndarray:
    """Vectorised trilinear interpolation of a 3D LUT over an image.

    Args:
        image: float32 array, shape (H, W, 3), values in [0, 1], BGR channel order.
        lut_data: Parsed CubeData with table indexed [B, G, R, channel].

    Returns:
        float32 array same shape, values in [0, 1].
    """
    size = lut_data.lut_size
    table = lut_data.table  # (size, size, size, 3)

    coords = image * (size - 1)  # (H, W, 3), float in [0, size-1]

    i0 = np.clip(np.floor(coords).astype(np.int32), 0, size - 2)
    i1 = i0 + 1
    frac = (coords - i0).astype(np.float32)  # (H, W, 3)

    b0, g0, r0 = i0[..., 0], i0[..., 1], i0[..., 2]
    b1, g1, r1 = i1[..., 0], i1[..., 1], i1[..., 2]
    fb = frac[..., 0, np.newaxis]
    fg = frac[..., 1, np.newaxis]
    fr = frac[..., 2, np.newaxis]

    c000 = table[b0, g0, r0]
    c001 = table[b0, g0, r1]
    c010 = table[b0, g1, r0]
    c011 = table[b0, g1, r1]
    c100 = table[b1, g0, r0]
    c101 = table[b1, g0, r1]
    c110 = table[b1, g1, r0]
    c111 = table[b1, g1, r1]

    result = (
        c000 * (1 - fb) * (1 - fg) * (1 - fr)
        + c001 * (1 - fb) * (1 - fg) * fr
        + c010 * (1 - fb) * fg * (1 - fr)
        + c011 * (1 - fb) * fg * fr
        + c100 * fb * (1 - fg) * (1 - fr)
        + c101 * fb * (1 - fg) * fr
        + c110 * fb * fg * (1 - fr)
        + c111 * fb * fg * fr
    )
    return result
