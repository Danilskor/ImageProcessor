import cv2
import numpy as np
from PySide6.QtCore import QObject, QThread, QTimer, Signal, Slot


class _Worker(QObject):
    done = Signal(object, object, int)  # (result, thumbnails_dict, generation)

    def __init__(self, pipeline, image: np.ndarray, generation: int):
        super().__init__()
        self._pipeline = pipeline
        self._image = image
        self._generation = generation

    @Slot()
    def run(self) -> None:
        result, thumbnails = self._pipeline.process_with_thumbnails(self._image)
        self.done.emit(result, thumbnails, self._generation)


class AppController(QObject):
    image_processed = Signal(object)    # np.ndarray
    thumbnails_ready = Signal(object)   # dict[str, np.ndarray]

    DEBOUNCE_MS = 150

    def __init__(self, pipeline, parent=None):
        super().__init__(parent)
        self._pipeline = pipeline
        self._original: np.ndarray | None = None
        self._generation: int = 0

        # Keep strong Python references to (thread, worker) pairs until the
        # thread finishes, so GC never deletes them mid-run.
        self._active: list[tuple[QThread, _Worker]] = []

        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.timeout.connect(self._run_pipeline)

    def load_image(self, path: str) -> None:
        image = cv2.imread(path)
        if image is None:
            raise OSError(f"Cannot load image: {path}")
        self._original = image
        self.request_update()

    def set_image(self, image: np.ndarray) -> None:
        self._original = image.copy()
        self.request_update()

    def request_update(self) -> None:
        self._debounce.start(self.DEBOUNCE_MS)

    def get_input_image_for(self, step_name: str) -> np.ndarray | None:
        """Return the image as it enters the named step (synchronous, main thread)."""
        if self._original is None:
            return None
        return self._pipeline.process_before(step_name, self._original.copy())

    def get_image_up_to(self, step_name: str) -> np.ndarray | None:
        """Return the image after the named step has been applied."""
        if self._original is None:
            return None
        return self._pipeline.process_up_to(step_name, self._original.copy())

    def save_image(self, path: str) -> None:
        if self._original is None:
            return
        result = self._pipeline.process(self._original.copy())
        cv2.imwrite(path, result)

    def _run_pipeline(self) -> None:
        if self._original is None:
            return

        self._generation += 1
        gen = self._generation

        worker = _Worker(self._pipeline, self._original.copy(), gen)
        thread = QThread(self)
        worker.moveToThread(thread)

        thread.started.connect(worker.run)
        worker.done.connect(self._on_worker_done)
        worker.done.connect(thread.quit)
        thread.finished.connect(self._purge_finished)

        self._active.append((thread, worker))
        thread.start()

    @Slot(object, object, int)
    def _on_worker_done(self, result: np.ndarray, thumbnails: dict, generation: int) -> None:
        if generation == self._generation:
            self.image_processed.emit(result)
            self.thumbnails_ready.emit(thumbnails)

    @Slot()
    def _purge_finished(self) -> None:
        self._active = [(t, w) for t, w in self._active if not t.isFinished()]
