from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator, QValidator
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QLayout,
)

from src.constants import RO_STYLESHEET, FIXED_WIDTH
from src.converter import (
    freqToDistance,
    freqToTime,
    distanceToTime,
    distanceToFreq,
    timeToFreq,
    timeToDistance,
    computeC,
)


class ConverterWidget(QWidget):
    """Class for converter widget tab."""

    converterWidgetName = "Converter"
    defaultTemperature = 20
    defaultFreq = 100

    def __init__(self, parent: QWidget = None) -> None:
        """Create widget and methods to convert values.

        We have:
        - one speed of sound layout depending on temperature,
        - two converter layouts to easily compare different setups.

        Conversion is frequency (Hz) - lambda (m) - period (T).
        """

        super().__init__(parent)

        # Main tab widget
        self.converterWidget = QWidget(parent)

        # Create layouts
        cLayout = CLayout(self, self.defaultTemperature)
        valuesLayout = ValuesLayout(self, self.defaultFreq, cLayout)

        # Main tab layout
        mainLayout = QVBoxLayout(self.converterWidget)
        for _ in range(5):  # top padding
            mainLayout.addWidget(QLabel(""))
        mainLayout.addLayout(cLayout.getLayout())
        mainLayout.addWidget(QLabel(""))  # mid padding
        mainLayout.addLayout(valuesLayout.getLayout())
        for _ in range(5):  # bot padding
            mainLayout.addWidget(QLabel(""))

    def getWidget(self) -> QWidget:
        """Return created QWidget."""

        return self.converterWidget

    def getWidgetName(self) -> QWidget:
        """Return widget name."""

        return self.converterWidgetName


class CLayout(QWidget):
    """Class for speed of sound (c) layout with all connections."""

    def __init__(self, parent: QWidget, defaultTemperature: float):
        """Define all widgets in layout and make connections."""

        super().__init__(parent)

        # Validators for user input
        temperatureValidator = QDoubleValidator()
        temperatureValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        temperatureValidator.setRange(-100, 100)
        temperatureValidator.setDecimals(2)
        cValidator = QIntValidator()
        cValidator.setRange(0, 400)

        # Values input
        self.temperature = getQLineEdit(FIXED_WIDTH, temperatureValidator)
        self.c = getQLineEdit(
            FIXED_WIDTH, cValidator, readOnly=True, styleSheet=RO_STYLESHEET
        )

        # Connections to update on each user input
        self.temperature.textChanged.connect(self._updateC)

        # Default values
        self.temperature.setText(f"{defaultTemperature}")
        self.defaultTemperature = defaultTemperature

        # Units
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
        self.cLayout = QHBoxLayout()
        for _ in range(5):  # spacing on the left
            self.cLayout.addWidget(QLabel())
        self.cLayout.addLayout(sosLabelsLayout)
        self.cLayout.addLayout(sosValuesLayout)
        self.cLayout.addLayout(sosUnitsLayout)
        for _ in range(5):  # spacing on the left
            self.cLayout.addWidget(QLabel())

    def getLayout(self) -> QLayout:
        """Return created layout."""

        return self.cLayout

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

    def checkTemperature(self):
        """Check that temperature is set so we have c.

        If not, then set it to default temperature.
        """

        if not self.temperature.text():
            self.temperature.setText(f"{self.defaultTemperature}")


class ValuesLayout(QWidget):
    """Class for conversion values layout, with all connections."""

    def __init__(self, parent: QWidget, defaultFreq: float, cLayout: CLayout) -> None:
        """Create layout and all connections with QLineEdit objects."""

        super().__init__(parent)

        # Reference to, not a copy
        self.cLayout = cLayout

        # Validators for user input
        distanceValidator = QDoubleValidator()
        distanceValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        distanceValidator.setRange(0, 10000)
        distanceValidator.setDecimals(2)
        timeValidator = QDoubleValidator()
        timeValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        timeValidator.setRange(0, 30000)
        timeValidator.setDecimals(3)
        freqValidator = QDoubleValidator()
        freqValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        freqValidator.setRange(0, 40000)
        freqValidator.setDecimals(2)

        # Values input
        self.distance = getQLineEdit(FIXED_WIDTH, distanceValidator)
        self.distance2 = getQLineEdit(
            FIXED_WIDTH, distanceValidator, readOnly=True, styleSheet=RO_STYLESHEET
        )
        self.distance4 = getQLineEdit(
            FIXED_WIDTH, distanceValidator, readOnly=True, styleSheet=RO_STYLESHEET
        )
        self.time = getQLineEdit(FIXED_WIDTH, timeValidator)
        self.time2 = getQLineEdit(
            FIXED_WIDTH, timeValidator, readOnly=True, styleSheet=RO_STYLESHEET
        )
        self.time4 = getQLineEdit(
            FIXED_WIDTH, timeValidator, readOnly=True, styleSheet=RO_STYLESHEET
        )
        self.freq = getQLineEdit(FIXED_WIDTH, freqValidator)

        # Connections to update on each user input
        self.distance.textChanged.connect(self._updateValuesFromDistance)
        self.time.textChanged.connect(self._updateValuesFromTime)
        self.freq.textChanged.connect(self._updateValuesFromFreq)

        # Default values
        self.freq.setText(f"{defaultFreq}")

        # Units
        distanceUnit = QLabel("m")
        timeUnit = QLabel("ms")
        freqUnit = QLabel("Hz")

        # Layouts for /4 and /2 values
        freqLayout = QVBoxLayout()
        freqLayout.addWidget(self.freq, alignment=Qt.AlignmentFlag.AlignRight)
        distanceLayout = QVBoxLayout()
        distanceLayout.addWidget(self.distance4, alignment=Qt.AlignmentFlag.AlignRight)
        distanceLayout.addWidget(self.distance, alignment=Qt.AlignmentFlag.AlignRight)
        distanceLayout.addWidget(self.distance2, alignment=Qt.AlignmentFlag.AlignRight)
        timeLayout = QVBoxLayout()
        timeLayout.addWidget(self.time4, alignment=Qt.AlignmentFlag.AlignRight)
        timeLayout.addWidget(self.time, alignment=Qt.AlignmentFlag.AlignRight)
        timeLayout.addWidget(self.time2, alignment=Qt.AlignmentFlag.AlignRight)

        # Layout for values line
        self.valuesLayout = QHBoxLayout()
        for _ in range(5):  # spacing on the left
            self.valuesLayout.addWidget(QLabel())
        self.valuesLayout.addLayout(freqLayout)
        self.valuesLayout.addWidget(freqUnit, alignment=Qt.AlignmentFlag.AlignLeft)
        self.valuesLayout.addLayout(distanceLayout)
        self.valuesLayout.addWidget(distanceUnit, alignment=Qt.AlignmentFlag.AlignLeft)
        self.valuesLayout.addLayout(timeLayout)
        self.valuesLayout.addWidget(timeUnit, alignment=Qt.AlignmentFlag.AlignLeft)
        for _ in range(5):  # spacing on the right
            self.valuesLayout.addWidget(QLabel())

    def getLayout(self) -> QLayout:
        """Return created layout."""

        return self.valuesLayout

    def _updateValuesFromDistance(self) -> None:
        """Update time and frequency values."""

        self.distance.setText(self.distance.text().replace(",", "."))

        # Check that we can convert correctly
        if not (self.distance.text() and float(self.distance.text())):
            self._resetTime()
            self._resetFreq()
            return

        # Check that speed of sound is set
        self.cLayout.checkTemperature()

        # Do all conversions from distance
        distance = float(self.distance.text())
        c = float(self.cLayout.c.text())

        # We disconnect before update to avoid infinite connect loop
        self.time.textChanged.disconnect(self._updateValuesFromTime)
        self.freq.textChanged.disconnect(self._updateValuesFromFreq)
        self.time.setText(f"{distanceToTime(distance, c)}")
        self.freq.setText(f"{distanceToFreq(distance, c)}")
        self.time.textChanged.connect(self._updateValuesFromTime)
        self.freq.textChanged.connect(self._updateValuesFromFreq)

        # Update by 2 and by 4 values
        self._updateValues24()

    def _updateValuesFromTime(self) -> None:
        """Update distance and frequency values."""

        self.time.setText(self.time.text().replace(",", "."))

        # Check that we can convert correctly
        if not (self.time.text() and float(self.time.text())):
            self._resetFreq()
            self._resetDistance()
            return

        # Check that speed of sound is set
        self.cLayout.checkTemperature()

        # Do all conversions from time
        time = float(self.time.text())
        c = float(self.cLayout.c.text())

        # We disconnect before update to avoid infinite connect loop
        self.distance.textChanged.disconnect(self._updateValuesFromDistance)
        self.freq.textChanged.disconnect(self._updateValuesFromFreq)
        self.distance.setText(f"{timeToDistance(time, c)}")
        self.freq.setText(f"{timeToFreq(time)}")
        self.distance.textChanged.connect(self._updateValuesFromDistance)
        self.freq.textChanged.connect(self._updateValuesFromFreq)

        # Update by 2 and by 4 values
        self._updateValues24()

    def _updateValuesFromFreq(self) -> None:
        """Update time and distance values."""

        self.freq.setText(self.freq.text().replace(",", "."))

        # Check that we can convert correctly
        if not (self.freq.text() and float(self.freq.text())):
            self._resetTime()
            self._resetDistance()
            return

        # Check that speed of sound is set
        self.cLayout.checkTemperature()

        # Do all conversions from freq
        freq = float(self.freq.text())
        c = float(self.cLayout.c.text())

        # We disconnect before update to avoid infinite connect loop
        self.distance.textChanged.disconnect(self._updateValuesFromDistance)
        self.time.textChanged.disconnect(self._updateValuesFromTime)
        self.distance.setText(f"{freqToDistance(freq, c)}")
        self.time.setText(f"{freqToTime(freq, c)}")
        self.distance.textChanged.connect(self._updateValuesFromDistance)
        self.time.textChanged.connect(self._updateValuesFromTime)

        # Update by 2 and by 4 values
        self._updateValues24()

    def _updateValues24(self) -> None:
        """Update by 2 and by 4 values."""

        self.distance2.setText(
            f"{Decimal(float(self.distance.text()) / 2).quantize(Decimal(".01"))}"
        )
        self.distance4.setText(
            f"{Decimal(float(self.distance.text()) / 4).quantize(Decimal(".01"))}"
        )
        self.time2.setText(
            f"{distanceToTime(float(self.distance2.text()), float(self.cLayout.c.text()))}"
        )
        self.time4.setText(
            f"{distanceToTime(float(self.distance4.text()), float(self.cLayout.c.text()))}"
        )

    def _resetTime(self) -> None:
        """Reset all times."""

        self.time.setText("")
        self.time2.setText("")
        self.time4.setText("")

    def _resetDistance(self) -> None:
        """Reset all distances."""

        self.distance.setText("")
        self.distance2.setText("")
        self.distance4.setText("")

    def _resetFreq(self) -> None:
        """Reset all freqs."""

        self.freq.setText("")


def getQLineEdit(
    fixedWidth: int, validator: QValidator, readOnly: bool = False, styleSheet: str = ""
) -> QLineEdit:
    """Return QLineEdit with given params."""

    qLineEdit = QLineEdit()
    qLineEdit.setFixedWidth(fixedWidth)
    qLineEdit.setValidator(validator)
    qLineEdit.setReadOnly(readOnly)
    qLineEdit.setStyleSheet(styleSheet)
    return qLineEdit
