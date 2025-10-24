import sys

from PySide6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QWidget,
    QTabWidget,
)

# Dark theme for Qt
import qdarktheme

# from src.ampGainWidget import AmpGainWidget
from src.limiterWidget import LimiterWidget


APP_NAME = "LimiterRMS"


class Window(QWidget):
    """Create widgets and their associated connections."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.setGeometry(400, 50, 900, 700)

        # Get widgets for tabs
        limiterWidget = LimiterWidget(self)
        # ampGainWidget = AmpGainWidget(self)

        # Create tab widget for future tools
        tab = QTabWidget(self)
        tab.addTab(limiterWidget.getWidget(), limiterWidget.getWidgetName())
        # tab.addTab(ampGainWidget, ampGainWidgetName)

        # Create main layout that will contains tabs
        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(tab)

        self.show()


def run() -> None:
    app = QApplication()
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
