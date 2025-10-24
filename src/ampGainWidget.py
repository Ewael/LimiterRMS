from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
)

from src.ampGain import AmpGain


class AmpGainWidget(QWidget):
    """Amplifier gain widget for associated tab."""

    fixedWidth = 68
    ampGainWidgetName = "Amplifier gain"

    def __init__(self, parent: QWidget = None) -> None:
        """Create widget and methods to return it."""

        super().__init__(parent)

        # Validators for user input
        ampGainFloatValidator = QDoubleValidator()
        ampGainFloatValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        ampGainFloatValidator.setRange(0, 500)
        ampGainFloatValidator.setDecimals(4)

        # How to correctly mesure amplifier gain
        sineWaveInfo = QLabel("Generate a 50Hz sine wave")
        sineWaveInfo.setStyleSheet("font-weight: bold")

        # Voltage IN and voltage OUT
        voltageInInfo = QLabel("Voltage value BEFORE amplification:")
        voltageOutInfo = QLabel("Voltage value AFTER amplification:")
        self.voltageInValue = QLineEdit()
        self.voltageInValue.setFixedWidth(self.fixedWidth)
        self.voltageInValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voltageInValue.setValidator(ampGainFloatValidator)
        self.voltageInValue.setToolTip("XLR - between pin 2 and pin 3")
        self.voltageOutValue = QLineEdit()
        self.voltageOutValue.setFixedWidth(self.fixedWidth)
        self.voltageOutValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voltageOutValue.setValidator(ampGainFloatValidator)
        self.voltageOutValue.setToolTip("SPK - between +x/-x (most of the time +1/-1)")
        voltageInUnit = QLabel("V")
        voltageOutUnit = QLabel("V")

        # Connection between user changing voltage value and amp gain updating
        self.voltageInValue.textChanged.connect(self._updateAmpGain)
        self.voltageOutValue.textChanged.connect(self._updateAmpGain)

        # Ampli gain
        ampliGainInfo = QLabel("Amplifier gain:")
        ampliGainInfo.setStyleSheet("color: red; font-weight: bold")
        self.ampliGainValue = QLineEdit()
        self.ampliGainValue.setFixedWidth(self.fixedWidth)
        self.ampliGainValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ampliGainValue.setReadOnly(True)  # ampli gain is read-only
        self.ampliGainValue.setStyleSheet(
            "background-color: #FFCCCC; color: red; font-weight: bold"
        )
        ampliGainUnit = QLabel("dB")
        ampliGainUnit.setStyleSheet("color: red; font-weight: bold")

        # Layout for informations about each value
        voltageInfoLayout = QVBoxLayout()
        voltageInfoLayout.addWidget(
            voltageInInfo, alignment=Qt.AlignmentFlag.AlignRight
        )
        voltageInfoLayout.addWidget(
            voltageOutInfo, alignment=Qt.AlignmentFlag.AlignRight
        )
        voltageInfoLayout.addWidget(
            ampliGainInfo, alignment=Qt.AlignmentFlag.AlignRight
        )

        # Layout to enter in and out voltages values for 50Hz sine wave
        voltageValuesLayout = QVBoxLayout()
        voltageValuesLayout.addWidget(
            self.voltageInValue, alignment=Qt.AlignmentFlag.AlignCenter
        )
        voltageValuesLayout.addWidget(
            self.voltageOutValue, alignment=Qt.AlignmentFlag.AlignCenter
        )
        voltageValuesLayout.addWidget(
            self.ampliGainValue, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Layout for units
        voltageUnitsLayout = QVBoxLayout()
        voltageUnitsLayout.addWidget(voltageInUnit)
        voltageUnitsLayout.addWidget(voltageOutUnit)
        voltageUnitsLayout.addWidget(ampliGainUnit)

        # Infos and values side by side layout
        infoAndValuesLayout = QHBoxLayout()
        for _ in range(10):  # spacing above
            infoAndValuesLayout.addWidget(QLabel())
        infoAndValuesLayout.addLayout(voltageInfoLayout)
        infoAndValuesLayout.addLayout(voltageValuesLayout)
        infoAndValuesLayout.addLayout(voltageUnitsLayout)
        for _ in range(10):  # spacing under
            infoAndValuesLayout.addWidget(QLabel())

        # Widget that will go in the tab
        self.ampGainWidget = QWidget(parent)

        # Ampli gain Widget layout
        ampGainLayout = QVBoxLayout(self.ampGainWidget)
        for _ in range(10):  # spacing above
            ampGainLayout.addWidget(QLabel())
        ampGainLayout.addWidget(sineWaveInfo, alignment=Qt.AlignmentFlag.AlignCenter)
        ampGainLayout.addLayout(infoAndValuesLayout)
        for _ in range(10):  # spacing under
            ampGainLayout.addWidget(QLabel())

    def getWidget(self) -> QWidget:
        """Return created QWidget."""

        return self.ampGainWidget

    def getWidgetName(self) -> str:
        """Return widget name."""

        return self.ampGainWidgetName

    def _updateAmpGain(self) -> None:
        """Update amplifier gain with current voltage values."""

        self.voltageInValue.setText(self.voltageInValue.text().replace(",", "."))
        self.voltageOutValue.setText(self.voltageOutValue.text().replace(",", "."))

        # We check that we have correct voltage values (not empty and not 0)
        if not (
            self.voltageInValue.text()
            and self.voltageOutValue.text()
            and float(self.voltageInValue.text())
            and float(self.voltageOutValue.text())
        ):
            self.ampliGainValue.setText("")
            return

        ampGain = AmpGain(
            float(self.voltageInValue.text()), float(self.voltageOutValue.text())
        )
        self.ampliGainValue.setText(f"{ampGain.computeAmpGain()}")
