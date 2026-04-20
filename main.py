import sys

from PySide6.QtWidgets import QApplication

from src.ui.main_window import MainWindow
from src.ui.theme import Theme, apply_theme


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("ImageProcessor")
    apply_theme(app, Theme.DARK)   # default: dark
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
