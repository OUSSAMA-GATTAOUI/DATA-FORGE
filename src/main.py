from __future__ import annotations
import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication


def _ensure_paths() -> None:
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.join(base, "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)


def main() -> None:
    _ensure_paths()

    from src.utils.styles import apply_app_style
    from src.login import LoginWindow

    app = QApplication(sys.argv)
    apply_app_style(app)

    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base, "icon.ico")
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    win = LoginWindow()
    win.setWindowIcon(app.windowIcon())
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

