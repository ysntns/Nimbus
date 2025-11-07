"""
GUI Entry Point - Launch PyQt6 application

Main entry point for the GUI application.
"""

import sys
from loguru import logger

try:
    from PyQt6.QtWidgets import QApplication
    from app.gui.main_window import MainWindow
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False
    logger.error("PyQt6 not available - install with: pip install PyQt6")


def main():
    """Launch GUI application."""
    if not PYQT6_AVAILABLE:
        print("ERROR: PyQt6 is not installed.")
        print("Install it with: pip install nimbus-backup[gui]")
        sys.exit(1)

    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Nimbus")
        app.setOrganizationName("Nimbus")

        window = MainWindow()
        window.show()

        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"GUI application failed: {e}")
        print(f"ERROR: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
