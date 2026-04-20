from typing import override

import cv2
import numpy as np

from src.base.base_processor import BaseProcessor, BaseProcessorConfig

HOUGH_MODES = ("standard", "probabilistic")


class HoughLinesConfig(BaseProcessorConfig):
    def __init__(
        self,
        mode: str = "standard",
        rho: float = 1.0,
        theta_deg: float = 1.0,
        threshold: int = 100,
        min_line_length: float = 50.0,
        max_line_gap: float = 10.0,
        line_color_bgr: tuple[int, int, int] = (0, 255, 0),
        line_thickness: int = 1,
    ):
        if mode not in HOUGH_MODES:
            raise ValueError(f"mode must be one of {HOUGH_MODES}")
        if rho <= 0:
            raise ValueError("rho must be positive")
        self.mode = mode
        self.rho = rho
        self.theta_deg = theta_deg
        self.threshold = threshold
        self.min_line_length = min_line_length
        self.max_line_gap = max_line_gap
        self.line_color_bgr = line_color_bgr
        self.line_thickness = line_thickness


class HoughLinesTransformation(BaseProcessor):
    """Detect lines via standard or probabilistic Hough transform.

    After each call to process(), the attributes below are updated:
      hough_space_image  — rho-theta accumulator visualised as a colour image
      edge_image         — Canny edge map used as input to the transform
      lines_count        — number of lines/segments detected
    """

    def __init__(
        self,
        mode: str = "standard",
        rho: float = 1.0,
        theta_deg: float = 1.0,
        threshold: int = 100,
        min_line_length: float = 50.0,
        max_line_gap: float = 10.0,
        line_color_bgr: tuple[int, int, int] = (0, 255, 0),
        line_thickness: int = 1,
    ):
        super().__init__()
        self._config = HoughLinesConfig(
            mode, rho, theta_deg, threshold,
            min_line_length, max_line_gap,
            line_color_bgr, line_thickness,
        )
        self.hough_space_image: np.ndarray | None = None
        self.edge_image: np.ndarray | None = None
        self.lines_count: int = 0
        self.hough_space_max_votes: int = 0

    @override
    def process(self, image: np.ndarray) -> np.ndarray:
        cfg = self._config
        theta = np.deg2rad(cfg.theta_deg)

        if image.ndim == 3:
            edges = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            edges = image
        # Treat any non-zero pixel as an edge
        edges = (edges > 0).astype(np.uint8) * 255
        self.edge_image = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        self.hough_space_image, self.hough_space_max_votes = _compute_hough_space(edges, cfg.rho, theta)

        overlay = image.copy()
        color = cfg.line_color_bgr
        thickness = cfg.line_thickness

        if cfg.mode == "standard":
            lines = cv2.HoughLines(edges, cfg.rho, theta, cfg.threshold)
            self.lines_count = len(lines) if lines is not None else 0
            if lines is not None:
                h, w = image.shape[:2]
                for line in lines:
                    rho_val, theta_val = line[0]
                    _draw_infinite_line(overlay, rho_val, theta_val, color, thickness, w, h)
        else:  # probabilistic
            lines = cv2.HoughLinesP(
                edges,
                cfg.rho,
                theta,
                cfg.threshold,
                minLineLength=cfg.min_line_length,
                maxLineGap=cfg.max_line_gap,
            )
            self.lines_count = len(lines) if lines is not None else 0
            if lines is not None:
                for seg in lines:
                    x1, y1, x2, y2 = seg[0]
                    cv2.line(overlay, (x1, y1), (x2, y2), color, thickness)

        return overlay


# ── Helpers ───────────────────────────────────────────────────────────────────

_MAX_EDGE_POINTS = 20_000  # cap for performance on large images


def _compute_hough_space(
    edges: np.ndarray,
    rho_res: float = 1.0,
    theta_res: float = np.pi / 180,
) -> tuple[np.ndarray, int]:
    """Return (colour accumulator image, max_votes).

    Axes: x = theta (0…π), y = rho (-diag…+diag).
    """
    h, w = edges.shape
    diag = int(np.ceil(np.sqrt(h * h + w * w)))
    num_rhos = int(2 * diag / rho_res) + 1
    thetas = np.arange(0.0, np.pi, theta_res)
    num_thetas = len(thetas)

    ys, xs = np.nonzero(edges)
    if len(xs) == 0:
        return np.zeros((num_rhos, num_thetas, 3), dtype=np.uint8), 0

    # Subsample if too many edge points
    if len(xs) > _MAX_EDGE_POINTS:
        idx = np.random.default_rng(0).choice(len(xs), _MAX_EDGE_POINTS, replace=False)
        xs, ys = xs[idx], ys[idx]

    cos_t = np.cos(thetas).astype(np.float32)   # (T,)
    sin_t = np.sin(thetas).astype(np.float32)   # (T,)

    # rho indices: (N, T)
    rho_vals = (
        xs[:, np.newaxis] * cos_t[np.newaxis, :]
        + ys[:, np.newaxis] * sin_t[np.newaxis, :]
    )
    rho_idx = np.clip(
        np.round(rho_vals / rho_res + diag / rho_res).astype(np.int32),
        0, num_rhos - 1,
    )
    theta_idx = np.broadcast_to(np.arange(num_thetas), rho_idx.shape)

    flat = rho_idx.ravel() * num_thetas + theta_idx.ravel()
    accumulator = np.bincount(flat, minlength=num_rhos * num_thetas)
    accumulator = accumulator.reshape(num_rhos, num_thetas).astype(np.float32)

    max_val = int(accumulator.max())
    if max_val > 0:
        vis = (accumulator / max_val * 255).astype(np.uint8)
    else:
        vis = np.zeros((num_rhos, num_thetas), dtype=np.uint8)

    return cv2.applyColorMap(vis, cv2.COLORMAP_HOT), max_val


def _draw_infinite_line(
    image: np.ndarray,
    rho: float,
    theta: float,
    color: tuple[int, int, int],
    thickness: int,
    w: int,
    h: int,
) -> None:
    """Draw a line parameterised by (rho, theta) clipped to the image bounds."""
    cos_t, sin_t = np.cos(theta), np.sin(theta)
    if abs(sin_t) > 1e-6:
        x0, x1 = 0, w - 1
        y0 = int((rho - x0 * cos_t) / sin_t)
        y1 = int((rho - x1 * cos_t) / sin_t)
    else:
        y0, y1 = 0, h - 1
        x0 = x1 = int(rho / cos_t)
    cv2.line(image, (x0, y0), (x1, y1), color, thickness)
