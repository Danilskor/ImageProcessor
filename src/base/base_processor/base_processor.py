import numpy as np
from .base_processor_config import BaseProcessorConfig


class BaseProcessor:
    def __init__(self):
        pass

    def process(self, image: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Subclasses must implement this method")

    def update_config(
        self, config: BaseProcessorConfig | None = None, **kwargs
    ) -> None:
        if config is not None:
            self._config = config
        if kwargs:
            self._config.update(**kwargs)
