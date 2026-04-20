import dataclasses

import cv2
import numpy as np

from src.base import PipelineError
from src.base.base_processor import BaseProcessor

_THUMB_LONG_SIDE = 160


@dataclasses.dataclass
class PipelineStep:
    name: str
    processor: BaseProcessor
    enabled: bool = True


class ProcessingPipeline:
    def __init__(self):
        self._steps: list[PipelineStep] = []

    def clear(self) -> None:
        self._steps.clear()

    def add_step(self, name: str, processor: BaseProcessor, enabled: bool = True) -> None:
        if any(s.name == name for s in self._steps):
            raise PipelineError(f"Step '{name}' already exists")
        self._steps.append(PipelineStep(name=name, processor=processor, enabled=enabled))

    def remove_step(self, name: str) -> None:
        step = self._get_step(name)
        self._steps.remove(step)

    def move_step(self, name: str, new_index: int) -> None:
        step = self._get_step(name)
        self._steps.remove(step)
        self._steps.insert(new_index, step)

    def set_step_enabled(self, name: str, enabled: bool) -> None:
        self._get_step(name).enabled = enabled

    def get_step(self, name: str) -> PipelineStep:
        return self._get_step(name)

    @property
    def steps(self) -> list[PipelineStep]:
        return list(self._steps)

    def process(self, image: np.ndarray) -> np.ndarray:
        result = image
        for step in self._steps:
            if step.enabled:
                result = step.processor.process(result)
        return result

    def process_up_to(self, name: str, image: np.ndarray) -> np.ndarray:
        """Process image through all steps up to and including the named step."""
        result = image
        for step in self._steps:
            if step.enabled:
                result = step.processor.process(result)
            if step.name == name:
                break
        return result

    def process_before(self, name: str, image: np.ndarray) -> np.ndarray:
        """Process image through all enabled steps that come BEFORE the named step."""
        result = image
        for step in self._steps:
            if step.name == name:
                break
            if step.enabled:
                result = step.processor.process(result)
        return result

    def process_with_thumbnails(
        self, image: np.ndarray
    ) -> tuple[np.ndarray, dict[str, np.ndarray]]:
        """Run pipeline, returning (final_image, {step_name: thumbnail_ndarray})."""
        result = image
        thumbs: dict[str, np.ndarray] = {}
        for step in self._steps:
            if step.enabled:
                result = step.processor.process(result)
            h, w = result.shape[:2]
            long = max(h, w)
            if long > _THUMB_LONG_SIDE:
                scale = _THUMB_LONG_SIDE / long
                rw, rh = max(1, int(w * scale)), max(1, int(h * scale))
                thumbs[step.name] = cv2.resize(result, (rw, rh), interpolation=cv2.INTER_AREA)
            else:
                thumbs[step.name] = result.copy()
        return result, thumbs

    def _get_step(self, name: str) -> PipelineStep:
        for step in self._steps:
            if step.name == name:
                return step
        raise PipelineError(f"Step '{name}' not found in pipeline")
