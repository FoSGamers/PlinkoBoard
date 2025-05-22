import pytest
from PySide6.QtWidgets import QApplication
from main import MainWindow
import sys

@pytest.fixture(scope="module")
def app():
    app = QApplication.instance() or QApplication(sys.argv)
    yield app

# Smoke test: main window launches
def test_mainwindow_launch(app):
    window = MainWindow()
    window.show()
    assert window.isVisible()
    window.close() 