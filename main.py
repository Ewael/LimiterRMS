import sys
import json

from decimal import Decimal, ROUND_DOWN, ROUND_UP
from math import log10, sqrt
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator
from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QComboBox,
)

from amplifier import Amplifier
from speaker import Speaker


OHM = "\u2126"
APP_NAME = "LimiterRMS"
AMPLIFIERS = r"amplifiers.json"
SPEAKERS = r"speakers.json"
BASE_PATH = str(Path(__file__).parent.resolve()) + "\\"


def getAmplisSpecs(path: str) -> dict[str, Amplifier]:
    """Return amplifiers specs from given JSON file.

    Only ['power']['8/4/2'] and ['outputs'] are optional and can be equal to None.
    """

    with open(path) as f:
        amplisData = json.load(f)
        amplisData.sort(key=lambda x: x["reference"])
    amplis = {}
    for ampli in amplisData:
        amplis[ampli["reference"]] = Amplifier(
            reference=ampli["reference"],
            gain=ampli["gain"],
            power={
                8: ampli["power"].get("8"),
                4: ampli["power"].get("4"),
                2: ampli["power"].get("2"),
            },
            outputs=ampli.get("outputs"),
        )
    return amplis


def getSpeakersSpecs(path: str) -> dict[str, Speaker]:
    """Return speakers specs from given JSON file.

    No optional values here.
    """

    with open(path) as f:
        speakersData = json.load(f)
        speakersData.sort(key=lambda x: x["reference"])
    speakers = {}
    for spk in speakersData:
        speakers[spk["reference"]] = Speaker(
            reference=spk["reference"],
            impedance=spk["impedance"],
            power=spk["power"],
            response=spk["response"],
            baffle=spk["baffle"],
        )
    return speakers


def limit(spk: Speaker, amp: Amplifier, impedance: int, sensitivity: float = 0.775) -> Decimal:
    """Compute threshold for given speaker, amplifier and impedance for 0.775V sensitivity."""

    # Update power values that we will use depending on current impedance
    spk_power = spk.power * (spk.impedance / impedance)
    amp_power = amp.power[impedance]

    lim_spk = (
        20 * log10(sqrt((spk_power / (1.5625 if spk.baffle == "OPEN" else 2.34375)) * impedance) / sensitivity)
        - amp.gain
    )
    lim_amp = 20 * log10(sqrt((amp_power / 2) * impedance) / sensitivity) - amp.gain
    lim = min(lim_spk, lim_amp)
    lim_dbU = Decimal(lim).quantize(Decimal(".1"), rounding=(ROUND_DOWN if lim > 0 else ROUND_UP))

    return lim_dbU


class Window(QWidget):
    """Create widgets and their associated connections."""

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.setGeometry(600, 300, 800, 500)

        # Get amplis and speakers data
        self.amplis = getAmplisSpecs(BASE_PATH + AMPLIFIERS)
        self.speakers = getSpeakersSpecs(BASE_PATH + SPEAKERS)

        # Amplis layout
        amplisColumnNameLabel = QLabel("Amplifiers")
        amplisColumnNameLabel.setStyleSheet("font-weight: bold")
        self.amplisListWidget = QListWidget()
        for ampli in self.amplis.values():
            item = QListWidgetItem(self.tr(ampli.reference))
            item.setToolTip(
                f"{ampli.reference}\n\n"
                + f"gain: {ampli.gain}dB\n"
                + f"power (8{OHM}): {str(ampli.power[8])+'W' if ampli.power[8] else 'Missing'}\n"
                + f"power (4{OHM}): {str(ampli.power[4])+'W' if ampli.power[4] else 'Missing'}\n"
                + f"power (2{OHM}): {str(ampli.power[2])+'W' if ampli.power[2] else 'Missing'}\n"
                + f"ouputs number: {ampli.outputs}"
            )
            self.amplisListWidget.addItem(item)
        self.amplisListWidget.setCurrentRow(0)
        self.amplisListWidget.setMinimumWidth(
            self._computeMinimumWidth(self.amplisListWidget) + self.amplisListWidget.frameWidth() * 10
        )
        self.amplisListWidget.setMinimumHeight(
            self.amplisListWidget.sizeHintForRow(0) * self.amplisListWidget.count()
            + 10 * self.amplisListWidget.frameWidth()
        )
        amplisSelectionLayout = QVBoxLayout()
        amplisSelectionLayout.addWidget(amplisColumnNameLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        amplisSelectionLayout.addWidget(self.amplisListWidget)

        # Speakers layout
        speakersColumnNameLabel = QLabel("Speakers")
        speakersColumnNameLabel.setStyleSheet("font-weight: bold")
        self.speakersListWidget = QListWidget()
        for speaker in self.speakers.values():
            item = QListWidgetItem(self.tr(speaker.reference))
            item.setToolTip(
                f"{speaker.reference}\n\n"
                + f"impedance: {speaker.impedance}{OHM}\n"
                + f"power ({speaker.impedance}{OHM}): {speaker.power}W\n"
                + f"frequency response: {speaker.response} Hz\n"
                + f"baffle: {speaker.baffle}"
            )
            self.speakersListWidget.addItem(item)
        self.speakersListWidget.setCurrentRow(0)
        self.speakersListWidget.setMinimumWidth(
            self._computeMinimumWidth(self.speakersListWidget) + self.speakersListWidget.frameWidth() * 10
        )
        self.speakersListWidget.setMinimumHeight(
            self.speakersListWidget.sizeHintForRow(0) * self.speakersListWidget.count()
            + 10 * self.speakersListWidget.frameWidth()
        )
        speakersSelectionLayout = QVBoxLayout()
        speakersSelectionLayout.addWidget(speakersColumnNameLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        speakersSelectionLayout.addWidget(self.speakersListWidget)

        # Impedance layout
        impedanceColumnNameLabel = QLabel("Impedance")
        impedanceColumnNameLabel.setStyleSheet("font-weight: bold")
        self.impedanceListWidget = QListWidget()
        for impedance in [2, 4, 8]:
            self.impedanceListWidget.addItem(QListWidgetItem(self.tr(str(impedance))))
        self.impedanceListWidget.setCurrentRow(0)
        self.impedanceListWidget.setMinimumWidth(
            self._computeMinimumWidth(self.impedanceListWidget) + self.impedanceListWidget.frameWidth() * 10
        )
        self.impedanceListWidget.setMinimumHeight(
            self.impedanceListWidget.sizeHintForRow(0) * self.impedanceListWidget.count()
            + 10 * self.impedanceListWidget.frameWidth()
        )
        impedanceSelectionLayout = QVBoxLayout()
        impedanceSelectionLayout.addWidget(impedanceColumnNameLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        impedanceSelectionLayout.addWidget(self.impedanceListWidget)

        # Selection layout
        selectionLayout = QHBoxLayout()
        selectionLayout.addLayout(amplisSelectionLayout)
        selectionLayout.addLayout(speakersSelectionLayout)
        selectionLayout.addLayout(impedanceSelectionLayout)

        # Selected labels
        speakerLabel = QLabel("Speaker")
        ampliLabel = QLabel("Amplifier")
        self.selectedSpeakerLabel = QLabel()
        self.selectedAmpliLabel = QLabel()

        # Selected layout
        recapSelectedLayout = QVBoxLayout()
        recapSelectedLayout.addWidget(QLabel())  # Empty for impedance row
        recapSelectedLayout.addWidget(speakerLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        recapSelectedLayout.addWidget(self.selectedSpeakerLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        recapSelectedLayout.addWidget(ampliLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        recapSelectedLayout.addWidget(self.selectedAmpliLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        recapSelectedLayout.addWidget(QLabel())  # Empty for treshold row

        # Recap labels
        impedanceLabel = QLabel("Impedance:")
        speakerBaffleLabel = QLabel("Baffle:")
        speakerPowerLabel = QLabel("Power:")
        ampliGainLabel = QLabel("Gain:")
        ampliPowerLabel = QLabel("Power:")
        tresholdLabel = QLabel("Treshold:")
        tresholdLabel.setStyleSheet("color: red; font-weight: bold")

        # Recap labels layout
        recapLabelsLayout = QVBoxLayout()
        recapLabelsLayout.addWidget(impedanceLabel, alignment=Qt.AlignmentFlag.AlignRight)
        recapLabelsLayout.addWidget(speakerBaffleLabel, alignment=Qt.AlignmentFlag.AlignRight)
        recapLabelsLayout.addWidget(speakerPowerLabel, alignment=Qt.AlignmentFlag.AlignRight)
        recapLabelsLayout.addWidget(ampliGainLabel, alignment=Qt.AlignmentFlag.AlignRight)
        recapLabelsLayout.addWidget(ampliPowerLabel, alignment=Qt.AlignmentFlag.AlignRight)
        recapLabelsLayout.addWidget(tresholdLabel, alignment=Qt.AlignmentFlag.AlignRight)

        # Validators for user input
        floatValidator = QDoubleValidator()
        floatValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        floatValidator.setRange(0, 100)
        floatValidator.setDecimals(2)
        intValidator = QIntValidator()
        intValidator.setRange(0, 50000)

        # Values input
        fixedWidth = 65
        self.impedanceValue = QLineEdit()
        self.impedanceValue.setFixedWidth(fixedWidth)
        self.impedanceValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.impedanceValue.setValidator(intValidator)
        self.speakerBaffleValue = QComboBox()
        self.speakerBaffleValue.setFixedWidth(fixedWidth)
        self.speakerBaffleValue.addItem("SEALED")
        self.speakerBaffleValue.addItem("OPEN")
        self.speakerPowerValue = QLineEdit()
        self.speakerPowerValue.setFixedWidth(fixedWidth)
        self.speakerPowerValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.speakerPowerValue.setValidator(intValidator)
        self.ampliGainValue = QLineEdit()
        self.ampliGainValue.setFixedWidth(fixedWidth)
        self.ampliGainValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ampliGainValue.setValidator(floatValidator)
        self.ampliPowerValue = QLineEdit()
        self.ampliPowerValue.setFixedWidth(fixedWidth)
        self.ampliPowerValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ampliPowerValue.setValidator(intValidator)
        self.tresholdValue = QLineEdit()
        self.tresholdValue.setFixedWidth(fixedWidth)
        self.tresholdValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.tresholdValue.setReadOnly(True)  # Treshold is read-only
        self.tresholdValue.setStyleSheet("background-color: #FFCCCC; color: red; font-weight: bold")

        # Layout for inputs
        recapInputsLayout = QVBoxLayout()
        recapInputsLayout.addWidget(self.impedanceValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapInputsLayout.addWidget(self.speakerBaffleValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapInputsLayout.addWidget(self.speakerPowerValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapInputsLayout.addWidget(self.ampliGainValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapInputsLayout.addWidget(self.ampliPowerValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapInputsLayout.addWidget(self.tresholdValue, alignment=Qt.AlignmentFlag.AlignLeft)

        # Units
        impedanceUnit = QLabel(f"{OHM}")
        speakerBaffleUnit = QLabel()  # No unit for baffle type
        speakerPowerUnit = QLabel("Watts AES")
        ampliGainUnit = QLabel("dB")
        ampliPowerUnit = QLabel("Watts RMS")
        tresholdUnit = QLabel("dBu")
        tresholdUnit.setStyleSheet("color: red; font-weight: bold")

        # Units layout
        recapUnitsLayout = QVBoxLayout()
        recapUnitsLayout.addWidget(impedanceUnit)
        recapUnitsLayout.addWidget(speakerBaffleUnit)
        recapUnitsLayout.addWidget(speakerPowerUnit)
        recapUnitsLayout.addWidget(ampliGainUnit)
        recapUnitsLayout.addWidget(ampliPowerUnit)
        recapUnitsLayout.addWidget(tresholdUnit)

        # Connections with labels and set default values at start
        self.amplisListWidget.itemSelectionChanged.connect(self._updateValues)
        self.speakersListWidget.itemSelectionChanged.connect(self._updateValues)
        self.impedanceListWidget.itemSelectionChanged.connect(self._updateValues)
        self._updateValues()

        # Recap layout
        recapLayoutLeft = QHBoxLayout()
        for _ in range(3):  # Spacers on the left
            recapLayoutLeft.addWidget(QLabel())
        recapLayoutLeft.addLayout(recapSelectedLayout)
        recapLayoutLeft.addLayout(recapLabelsLayout)
        recapLayoutRight = QHBoxLayout()
        recapLayoutRight.addLayout(recapInputsLayout)
        recapLayoutRight.addLayout(recapUnitsLayout)
        for _ in range(10):  # Spacers on the right
            recapLayoutRight.addWidget(QLabel())
        recapLayout = QHBoxLayout()
        recapLayout.addLayout(recapLayoutLeft)
        recapLayout.addLayout(recapLayoutRight)

        # Main layout
        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(selectionLayout)
        mainLayout.addLayout(recapLayout)
        self.setLayout(mainLayout)

        self.show()

    def _computeMinimumWidth(self, listWidget: QListWidget) -> int:
        """Return max length of a QListWidget so we have its minimum width."""

        res = listWidget.sizeHintForColumn(0)
        for i in range(listWidget.count()):
            if listWidget.sizeHintForColumn(i) > res:
                res = listWidget.sizeHintForColumn(i)
        return res

    def _updateValues(self):
        """Update value labels and treshold value."""

        # Get selected speaker, ampli and impedance
        spk = self.speakersListWidget.currentItem().text()
        ampli = self.amplisListWidget.currentItem().text()
        impedance = int(self.impedanceListWidget.currentItem().text())

        # Update selected labels
        self.selectedSpeakerLabel.setText(f"({spk})")
        self.selectedAmpliLabel.setText(f"({ampli})")

        # Check if configuration is possible, if not then switch to custom
        warning = ""
        if not self.amplis[ampli].power.get(impedance):  # Example: MA6.8Q does not support 2 Ohm
            self.ampliPowerValue.setText("")
            self.tresholdValue.setText("")
            powerWarning = f" Warning: {ampli} does not support {impedance} {OHM}"
            return
        if impedance > self.speakers[spk].impedance:  # Example: F221 cannot be 8 Ohm
            self.selectedSpeakerLabel.setText(f"(Custom)")
            impedanceWarning = f" (Warning: {spk} cannot be {impedance} {OHM})"

        # Get values and compute treshold
        speakerBaffle = self.speakers[spk].baffle
        speakerPower = int(self.speakers[spk].power * (self.speakers[spk].impedance / impedance))
        ampliGain = self.amplis[ampli].gain
        ampliPower = self.amplis[ampli].power[impedance]
        treshold = limit(self.speakers[spk], self.amplis[ampli], impedance)

        # Update value labels
        self.impedanceValue.setText(f"{impedance}")
        self.speakerBaffleValue.setCurrentText(f"{speakerBaffle}")
        self.speakerPowerValue.setText(f"{speakerPower}")
        self.ampliGainValue.setText(f"{ampliGain}")
        self.ampliPowerValue.setText(f"{ampliPower}")
        self.tresholdValue.setText(f"{treshold}")


def run() -> None:
    app = QApplication()
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
