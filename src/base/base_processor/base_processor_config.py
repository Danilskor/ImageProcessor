import dataclasses


@dataclasses.dataclass
class BaseProcessorConfig:
    def update(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if not hasattr(self, key):
                raise AttributeError(f"Unknown config parameter: '{key}'")
            setattr(self, key, value)
