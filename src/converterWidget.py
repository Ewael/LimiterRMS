from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
)

from src.converter import freqToDistance, distanceToTime, timeToFreq, computeC


class ConverterWidget(QWidget):
    """Class for converter widget tab."""

    fixedWidth = 68
    converterWidgetName = "Converter"
    defaultTemperature = 20

    def __init__(self, parent: QWidget = None) -> None:
        """Create widget and methods to convert values."""

        super().__init__(parent)

        # Validators for user input
        distanceValidator = QDoubleValidator()
        distanceValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        distanceValidator.setRange(0, 10000)
        distanceValidator.setDecimals(2)
        timeValidator = QDoubleValidator()
        timeValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        timeValidator.setRange(0, 30000)
        timeValidator.setDecimals(3)
        freqValidator = QIntValidator()
        freqValidator.setRange(0, 40000)
        temperatureValidator = QDoubleValidator()
        temperatureValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        temperatureValidator.setRange(-100, 100)
        temperatureValidator.setDecimals(2)
        cValidator = QIntValidator()
        cValidator.setRange(0, 400)

        # Values input
        self.distance = QLineEdit()
        self.distance.setFixedWidth(self.fixedWidth)
        self.distance.setValidator(distanceValidator)
        self.time = QLineEdit()
        self.time.setFixedWidth(self.fixedWidth)
        self.time.setValidator(timeValidator)
        self.freq = QLineEdit()
        self.freq.setFixedWidth(self.fixedWidth)
        self.freq.setValidator(freqValidator)
        self.temperature = QLineEdit()
        self.temperature.setFixedWidth(self.fixedWidth)
        self.temperature.setValidator(temperatureValidator)
        self.temperature.setText(f"{self.defaultTemperature}")
        self.c = QLineEdit()
        self.c.setFixedWidth(self.fixedWidth)
        self.c.setValidator(cValidator)
        self.c.setStyleSheet("background-color: #FFCCCC; color: red; font-weight: bold")

        # Connections to update on each user input
        self.distance.textChanged.connect(self._updateValuesFromDistance)
        self.time.textChanged.connect(self._updateValuesFromTime)
        self.freq.textChanged.connect(self._updateValuesFromFreq)
        self.temperature.textChanged.connect(self._updateC)
        self._updateC()

        # Units
        distanceUnit = QLabel("m")
        timeUnit = QLabel("ms")
        freqUnit = QLabel("Hz")
        temperatureUnit = QLabel("℃")
        cUnit = QLabel("m.s-1")

        # Labels for speed of sound
        temperatureLabel = QLabel("Temperature: ")
        cLabel = QLabel("Speed of sound (in air): ")

        # Speed of sound labels layout
        sosLabelsLayout = QVBoxLayout()
        sosLabelsLayout.addWidget(
            temperatureLabel, alignment=Qt.AlignmentFlag.AlignRight
        )
        sosLabelsLayout.addWidget(cLabel, alignment=Qt.AlignmentFlag.AlignRight)

        # Speed of sound values layout
        sosValuesLayout = QVBoxLayout()
        sosValuesLayout.addWidget(
            self.temperature, alignment=Qt.AlignmentFlag.AlignCenter
        )
        sosValuesLayout.addWidget(self.c, alignment=Qt.AlignmentFlag.AlignCenter)

        # Speed of sound units layout
        sosUnitsLayout = QVBoxLayout()
        sosUnitsLayout.addWidget(temperatureUnit, alignment=Qt.AlignmentFlag.AlignLeft)
        sosUnitsLayout.addWidget(cUnit, alignment=Qt.AlignmentFlag.AlignLeft)

        # Speed of sound main layout (with padding)
        sosLayout = QHBoxLayout()
        for _ in range(5):  # spacing on the left
            sosLayout.addWidget(QLabel())
        sosLayout.addLayout(sosLabelsLayout)
        sosLayout.addLayout(sosValuesLayout)
        sosLayout.addLayout(sosUnitsLayout)
        for _ in range(5):  # spacing on the left
            sosLayout.addWidget(QLabel())

        # Layout for values line
        valuesLayout = QHBoxLayout()
        for _ in range(5):  # spacing on the left
            valuesLayout.addWidget(QLabel())
        valuesLayout.addWidget(self.freq, alignment=Qt.AlignmentFlag.AlignRight)
        valuesLayout.addWidget(freqUnit, alignment=Qt.AlignmentFlag.AlignLeft)
        valuesLayout.addWidget(self.distance, alignment=Qt.AlignmentFlag.AlignRight)
        valuesLayout.addWidget(distanceUnit, alignment=Qt.AlignmentFlag.AlignLeft)
        valuesLayout.addWidget(self.time, alignment=Qt.AlignmentFlag.AlignRight)
        valuesLayout.addWidget(timeUnit, alignment=Qt.AlignmentFlag.AlignLeft)
        for _ in range(5):  # spacing on the right
            valuesLayout.addWidget(QLabel())

        # Main tab widget
        self.converterWidget = QWidget(parent)

        # Main tab layout
        mainLayout = QVBoxLayout(self.converterWidget)
        for _ in range(5):  # top padding
            mainLayout.addWidget(QLabel(""))
        mainLayout.addLayout(sosLayout)
        mainLayout.addLayout(valuesLayout)
        for _ in range(5):  # bot padding
            mainLayout.addWidget(QLabel(""))

    def getWidget(self) -> QWidget:
        """Return created QWidget."""

        return self.converterWidget

    def getWidgetName(self) -> QWidget:
        """Return widget name."""

        return self.converterWidgetName

    def _updateValuesFromDistance(self) -> None:
        """Update time and frequency values."""

        self.distance.setText(self.distance.text().replace(",", "."))

        # Check that we can convert correctly
        if not (self.distance.text() and float(self.distance.text())):
            self.time.setText("")
            self.freq.setText("")
            return

        # Check that speed of sound is set
        self._checkTemperature()

        # Do all conversions from distance
        distance = float(self.distance.text())
        time = distanceToTime(float(distance), float(self.c.text()))
        freq = timeToFreq(float(time))

        # We disconnect before update to avoid infinite connect loop
        self.time.textChanged.disconnect(self._updateValuesFromTime)
        self.freq.textChanged.disconnect(self._updateValuesFromFreq)
        self.time.setText(f"{time}")
        self.freq.setText(f"{freq}")
        self.time.textChanged.connect(self._updateValuesFromTime)
        self.freq.textChanged.connect(self._updateValuesFromFreq)

    def _updateValuesFromTime(self) -> None:
        """Update distance and frequency values."""

        self.time.setText(self.time.text().replace(",", "."))

        # Check that we can convert correctly
        if not (self.time.text() and float(self.time.text())):
            self.distance.setText("")
            self.freq.setText("")
            return

        # Check that speed of sound is set
        self._checkTemperature()

        # Do all conversions from time
        time = float(self.time.text())
        freq = timeToFreq(float(time))
        distance = freqToDistance(freq, float(self.c.text()))

        # We disconnect before update to avoid infinite connect loop
        self.distance.textChanged.disconnect(self._updateValuesFromDistance)
        self.freq.textChanged.disconnect(self._updateValuesFromFreq)
        self.distance.setText(f"{distance}")
        self.freq.setText(f"{freq}")
        self.distance.textChanged.connect(self._updateValuesFromDistance)
        self.freq.textChanged.connect(self._updateValuesFromFreq)

    def _updateValuesFromFreq(self) -> None:
        """Update time and distance values."""

        self.freq.setText(self.freq.text().replace(",", "."))

        # Check that we can convert correctly
        if not (self.freq.text() and int(self.freq.text())):
            self.distance.setText("")
            self.time.setText("")
            return

        # Check that speed of sound is set
        self._checkTemperature()

        # Do all conversions from freq
        freq = int(self.freq.text())
        distance = freqToDistance(freq, float(self.c.text()))
        time = distanceToTime(float(distance), float(self.c.text()))

        # We disconnect before update to avoid infinite connect loop
        self.distance.textChanged.disconnect(self._updateValuesFromDistance)
        self.time.textChanged.disconnect(self._updateValuesFromTime)
        self.distance.setText(f"{distance}")
        self.time.setText(f"{time}")
        self.distance.textChanged.connect(self._updateValuesFromDistance)
        self.time.textChanged.connect(self._updateValuesFromTime)

    def _updateC(self) -> None:
        """Update speed of sound (m.s-1)."""

        if (not self.temperature.text()) or self.temperature.text() == "-":
            self.c.setText("")
            return

        self.temperature.setText(self.temperature.text().replace(",", "."))
        if self.temperature.text()[0] == "-":
            temperature = -1 * float(self.temperature.text()[1:])
        else:
            temperature = float(self.temperature.text())

        self.c.setText(f"{computeC(temperature)}")

    def _checkTemperature(self):
        """Check that temperature is set so we have c.

        If not, then set it to default temperature.
        """

        if not self.temperature.text():
            self.temperature.setText(f"{self.defaultTemperature}")
