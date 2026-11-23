"""Application entry point."""
import sys

from PySide6.QtWidgets import QApplication

from ui import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Buoy Detection System")
    app.setOrganizationName("Local ASV Project")
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
