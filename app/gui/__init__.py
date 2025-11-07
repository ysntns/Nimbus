"""
Graphical User Interface for Nimbus.

PyQt6-based GUI application for visual backup management.
"""

try:
    from app.gui.main import main
    from app.gui.main_window import MainWindow
    __all__ = ['main', 'MainWindow']
except ImportError:
    # PyQt6 not installed
    __all__ = []
