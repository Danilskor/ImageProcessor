from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.pipeline import ProcessingPipeline, PipelineStep


class _StepRow(QWidget):
    toggled = Signal(str, bool)    # (name, enabled)
    selected = Signal(str)         # name

    def __init__(self, step: PipelineStep, parent=None):
        super().__init__(parent)
        self._name = step.name
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)

        self._check = QCheckBox()
        self._check.setChecked(step.enabled)
        self._check.stateChanged.connect(
            lambda state: self.toggled.emit(self._name, bool(state))
        )

        self._label = QLabel(step.name)

        layout.addWidget(self._check)
        layout.addWidget(self._label, stretch=1)

    def mousePressEvent(self, event) -> None:
        self.selected.emit(self._name)
        super().mousePressEvent(event)


class PipelinePanel(QWidget):
    step_selected = Signal(str)                    # name of selected step
    step_toggled = Signal(str, bool)               # (name, enabled)
    step_remove_requested = Signal(str)            # name
    order_changed = Signal()                       # steps were reordered
    add_step_requested = Signal(str, object)       # (label, processor_cls)

    def __init__(
        self,
        pipeline: ProcessingPipeline,
        add_menu_spec: dict | None = None,
        parent=None,
    ):
        """
        add_menu_spec: same structure as _ADD_STEP_MENU in main_window —
            {"Category": [("Label", ProcessorClass), ...], ...}
        """
        super().__init__(parent)
        self._pipeline = pipeline
        self._add_menu_spec = add_menu_spec or {}
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(6, 6, 6, 6)

        # Header row: title + add button
        header = QHBoxLayout()
        title = QLabel("Pipeline steps")
        title.setStyleSheet("font-weight: 600; font-size: 12px;")

        self._add_btn = QToolButton()
        self._add_btn.setText("+  Add step")
        self._add_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._add_btn.setObjectName("accent_btn")
        self._add_btn.setStyleSheet(
            "QToolButton { padding: 4px 10px; border-radius: 5px; font-weight: 600; }"
            "QToolButton::menu-indicator { width: 0; image: none; }"
        )
        self._rebuild_add_menu()

        header.addWidget(title, stretch=1)
        header.addWidget(self._add_btn)
        layout.addLayout(header)

        # Step list
        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._row_changed)
        layout.addWidget(self._list)

        # Move / remove buttons
        btn_row = QHBoxLayout()
        self._up_btn = QPushButton("▲")
        self._down_btn = QPushButton("▼")
        remove_btn = QPushButton("Remove")

        self._up_btn.setFixedWidth(36)
        self._down_btn.setFixedWidth(36)

        self._up_btn.clicked.connect(self._move_up)
        self._down_btn.clicked.connect(self._move_down)
        remove_btn.clicked.connect(self._remove_selected)

        btn_row.addWidget(self._up_btn)
        btn_row.addWidget(self._down_btn)
        btn_row.addStretch()
        btn_row.addWidget(remove_btn)
        layout.addLayout(btn_row)

    def _rebuild_add_menu(self) -> None:
        menu = QMenu(self)
        for category, entries in self._add_menu_spec.items():
            cat_menu = menu.addMenu(category)
            for label, processor_cls in entries:
                act = cat_menu.addAction(label)
                act.triggered.connect(
                    lambda checked=False, lbl=label, cls=processor_cls:
                        self.add_step_requested.emit(lbl, cls)
                )
        self._add_btn.setMenu(menu)

    def set_add_menu_spec(self, spec: dict) -> None:
        self._add_menu_spec = spec
        self._rebuild_add_menu()

    def refresh(self) -> None:
        current_row = self._list.currentRow()
        self._list.clear()
        for step in self._pipeline.steps:
            item = QListWidgetItem()
            row = _StepRow(step)
            row.toggled.connect(self._on_toggled)
            row.selected.connect(self.step_selected)
            self._list.addItem(item)
            self._list.setItemWidget(item, row)
            item.setSizeHint(row.sizeHint())

        count = self._list.count()
        if count > 0:
            self._list.setCurrentRow(max(0, min(current_row, count - 1)))

    def _row_changed(self, row: int) -> None:
        steps = self._pipeline.steps
        if 0 <= row < len(steps):
            self.step_selected.emit(steps[row].name)

    def _on_toggled(self, name: str, enabled: bool) -> None:
        self._pipeline.set_step_enabled(name, enabled)
        self.step_toggled.emit(name, enabled)

    def _move_up(self) -> None:
        row = self._list.currentRow()
        if row <= 0:
            return
        steps = self._pipeline.steps
        if row >= len(steps):
            return
        self._pipeline.move_step(steps[row].name, row - 1)
        self.refresh()
        self._list.setCurrentRow(row - 1)
        self.order_changed.emit()

    def _move_down(self) -> None:
        row = self._list.currentRow()
        steps = self._pipeline.steps
        if row < 0 or row >= len(steps) - 1:
            return
        self._pipeline.move_step(steps[row].name, row + 1)
        self.refresh()
        self._list.setCurrentRow(row + 1)
        self.order_changed.emit()

    def _remove_selected(self) -> None:
        row = self._list.currentRow()
        steps = self._pipeline.steps
        if 0 <= row < len(steps):
            name = steps[row].name
            self._pipeline.remove_step(name)
            self.refresh()
            self.step_remove_requested.emit(name)
