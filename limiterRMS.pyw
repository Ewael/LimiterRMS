import sys
import json

from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator, QIntValidator, QMouseEvent
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
    QTabWidget,
)

# Dark theme for Qt
import qdarktheme

from src.amplifier import Amplifier
from src.limiter import Limiter
from src.speaker import Speaker


OHM = "\u2126"
APP_NAME = "LimiterRMS"
AMPLIFIERS = r"amplifiers.json"
SPEAKERS = r"speakers.json"
BASE_PATH = str(Path(__file__).parent.resolve()) + "\\json\\"


def getAmplisSpecs(path: str) -> dict[str, Amplifier]:
    """Return amplifiers specs from given JSON file.

    For instance:
        {
            "reference": "Admark K420",
            "gain": 41,
            "power": {
                "8": 2000, [Optional]
                "4": 3400, [Optional]
                "2": 4760, [Optional]
                "8 (bridge)": 6800, [Optional]
                "4 (bridge)": 9520 [Optional]
            },
            "outputs": 4 [Optional]
        }
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
                "8": ampli["power"].get("8"),
                "4": ampli["power"].get("4"),
                "2": ampli["power"].get("2"),
                "8 (bridge)": ampli["power"].get("8 (bridge)"),
                "4 (bridge)": ampli["power"].get("4 (bridge)"),
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


class Window(QWidget):
    """Create widgets and their associated connections."""

    impedanceUnit = f"{OHM}"
    speakerPowerUnit = "Watt AES"
    ampliGainUnit = "dB"
    ampliPowerUnit = "Watt RMS"
    thresholdUnit = "dBu"

    customText = "[Custom]"

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.setGeometry(400, 50, 900, 700)

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
                + f"power (8{OHM}): {str(ampli.power["8"])+'W' if ampli.power["8"] else 'Missing'}\n"
                + f"power (4{OHM}): {str(ampli.power["4"])+'W' if ampli.power["4"] else 'Missing'}\n"
                + f"power (2{OHM}): {str(ampli.power["2"])+'W' if ampli.power["2"] else 'Missing'}\n"
                + f"bridge (8{OHM}): {str(ampli.power["8 (bridge)"])+'W' if ampli.power["8 (bridge)"] else 'Missing'}\n"
                + f"bridge (4{OHM}): {str(ampli.power["4 (bridge)"])+'W' if ampli.power["4 (bridge)"] else 'Missing'}\n"
                + f"ouputs number: {ampli.outputs}"
            )
            self.amplisListWidget.addItem(item)
        self.amplisListWidget.setCurrentRow(0)
        self.amplisListWidget.setMinimumWidth(
            self._computeMinimumWidth(self.amplisListWidget)
            + self.amplisListWidget.frameWidth() * 10
        )
        self.amplisListWidget.setMinimumHeight(
            self.amplisListWidget.sizeHintForRow(0) * 10
            + 10 * self.amplisListWidget.frameWidth()
        )
        amplisSelectionLayout = QVBoxLayout()
        amplisSelectionLayout.addWidget(
            amplisColumnNameLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
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
            self._computeMinimumWidth(self.speakersListWidget)
            + self.speakersListWidget.frameWidth() * 10
        )
        self.speakersListWidget.setMinimumHeight(
            self.speakersListWidget.sizeHintForRow(0) * 10
            + 10 * self.speakersListWidget.frameWidth()
        )
        speakersSelectionLayout = QVBoxLayout()
        speakersSelectionLayout.addWidget(
            speakersColumnNameLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
        speakersSelectionLayout.addWidget(self.speakersListWidget)

        # Impedance layout
        impedanceColumnNameLabel = QLabel("Impedance")
        impedanceColumnNameLabel.setStyleSheet("font-weight: bold")
        self.impedanceListWidget = QListWidget()
        for impedance in ["8", "4", "2", "8 (bridge)", "4 (bridge)"]:
            self.impedanceListWidget.addItem(QListWidgetItem(self.tr(impedance)))
        self.impedanceListWidget.setCurrentRow(0)
        self.impedanceListWidget.setMinimumWidth(
            self._computeMinimumWidth(self.impedanceListWidget)
            + self.impedanceListWidget.frameWidth() * 10
        )
        self.impedanceListWidget.setMinimumHeight(
            self.impedanceListWidget.sizeHintForRow(0) * 10
            + 10 * self.impedanceListWidget.frameWidth()
        )
        impedanceSelectionLayout = QVBoxLayout()
        impedanceSelectionLayout.addWidget(
            impedanceColumnNameLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
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
        recapSelectedLayout.addWidget(
            speakerLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
        recapSelectedLayout.addWidget(
            self.selectedSpeakerLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
        recapSelectedLayout.addWidget(
            ampliLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
        recapSelectedLayout.addWidget(
            self.selectedAmpliLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )
        recapSelectedLayout.addWidget(QLabel())  # Empty for threshold row

        # Recap labels
        impedanceLabel = QLabel("Impedance:")
        speakerBaffleLabel = QLabel("Baffle:")
        speakerPowerLabel = QLabel("Power:")
        ampliGainLabel = QLabel("Gain:")
        ampliPowerLabel = QLabel("Power:")
        thresholdLabel = QLabel("Threshold:")
        thresholdLabel.setStyleSheet("color: red; font-weight: bold")

        # Recap labels layout
        recapLabelsLayout = QVBoxLayout()
        recapLabelsLayout.addWidget(
            impedanceLabel, alignment=Qt.AlignmentFlag.AlignRight
        )
        recapLabelsLayout.addWidget(
            speakerBaffleLabel, alignment=Qt.AlignmentFlag.AlignRight
        )
        recapLabelsLayout.addWidget(
            speakerPowerLabel, alignment=Qt.AlignmentFlag.AlignRight
        )
        recapLabelsLayout.addWidget(
            ampliGainLabel, alignment=Qt.AlignmentFlag.AlignRight
        )
        recapLabelsLayout.addWidget(
            ampliPowerLabel, alignment=Qt.AlignmentFlag.AlignRight
        )
        recapLabelsLayout.addWidget(
            thresholdLabel, alignment=Qt.AlignmentFlag.AlignRight
        )

        # Validators for user input
        floatValidator = QDoubleValidator()
        floatValidator.setNotation(QDoubleValidator.Notation.StandardNotation)
        floatValidator.setRange(0, 100)
        floatValidator.setDecimals(2)
        intValidator = QIntValidator()
        intValidator.setRange(0, 50000)

        # Values input
        fixedWidth = 68
        self.impedanceValue = QLineEdit()
        self.impedanceValue.setFixedWidth(fixedWidth)
        self.impedanceValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.impedanceValue.setValidator(intValidator)
        self.speakerBaffleValue = QComboBox()
        self.speakerBaffleValue.setFixedWidth(fixedWidth)
        self.speakerBaffleValue.addItem("CLOSED")
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
        self.thresholdValue = QLineEdit()
        self.thresholdValue.setFixedWidth(fixedWidth)
        self.thresholdValue.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.thresholdValue.setReadOnly(True)  # threshold is read-only
        self.thresholdValue.setStyleSheet(
            "background-color: #FFCCCC; color: red; font-weight: bold"
        )

        # Layout for inputs
        recapInputsLayout = QVBoxLayout()
        recapInputsLayout.addWidget(
            self.impedanceValue, alignment=Qt.AlignmentFlag.AlignLeft
        )
        recapInputsLayout.addWidget(
            self.speakerBaffleValue, alignment=Qt.AlignmentFlag.AlignLeft
        )
        recapInputsLayout.addWidget(
            self.speakerPowerValue, alignment=Qt.AlignmentFlag.AlignLeft
        )
        recapInputsLayout.addWidget(
            self.ampliGainValue, alignment=Qt.AlignmentFlag.AlignLeft
        )
        recapInputsLayout.addWidget(
            self.ampliPowerValue, alignment=Qt.AlignmentFlag.AlignLeft
        )
        recapInputsLayout.addWidget(
            self.thresholdValue, alignment=Qt.AlignmentFlag.AlignLeft
        )

        # Units labels
        impedanceUnitLabel = QLabel(self.impedanceUnit)
        speakerBaffleUnitLabel = QLabel()  # No unit for baffle type
        speakerPowerUnitLabel = QLabel(self.speakerPowerUnit)
        ampliGainUnitLabel = QLabel(self.ampliGainUnit)
        ampliPowerUnitLabel = QLabel(self.ampliPowerUnit)
        thresholdUnitLabel = QLabel(self.thresholdUnit)
        thresholdUnitLabel.setStyleSheet("color: red; font-weight: bold")

        # Units layout
        recapUnitsLayout = QVBoxLayout()
        recapUnitsLayout.addWidget(impedanceUnitLabel)
        recapUnitsLayout.addWidget(speakerBaffleUnitLabel)
        recapUnitsLayout.addWidget(speakerPowerUnitLabel)
        recapUnitsLayout.addWidget(ampliGainUnitLabel)
        recapUnitsLayout.addWidget(ampliPowerUnitLabel)
        recapUnitsLayout.addWidget(thresholdUnitLabel)

        # Connections with labels and set default values at start
        self.amplisListWidget.itemSelectionChanged.connect(self._updateOnSelection)
        self.speakersListWidget.itemSelectionChanged.connect(self._updateOnSelection)
        self.impedanceListWidget.itemSelectionChanged.connect(self._updateOnSelection)
        self._updateOnSelection()

        # Anytime a value changes we update threshold
        self.impedanceValue.textChanged.connect(self._updatethreshold)
        self.speakerBaffleValue.currentTextChanged.connect(self._updateOnInputsSpeaker)
        self.speakerPowerValue.textChanged.connect(self._updateOnInputsSpeaker)
        self.ampliGainValue.textChanged.connect(self._updateOnInputsAmpli)
        self.ampliPowerValue.textChanged.connect(self._updateOnInputsAmpli)

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

        # Create QWidget for Limiter tab
        limiterWidget = QWidget(self)
        limiterWidgetName = "LimiterRMS"

        # Limiter Widget layout
        mainLayout = QVBoxLayout(limiterWidget)
        mainLayout.addLayout(selectionLayout)
        mainLayout.addLayout(recapLayout)
        limiterWidget.setLayout(mainLayout)
        
        # Create tab widget for future tools
        tab = QTabWidget(self)
        tab.addTab(limiterWidget, limiterWidgetName)

        self.show()

    def _computeMinimumWidth(self, listWidget: QListWidget) -> int:
        """Return max length of a QListWidget so we have its minimum width."""

        res = listWidget.sizeHintForColumn(0)
        for i in range(listWidget.count()):
            if listWidget.sizeHintForColumn(i) > res:
                res = listWidget.sizeHintForColumn(i)
        return res

    def _updateOnSelection(self) -> None:
        """Update value labels."""

        # Get selected speaker, ampli and impedance
        spk = self.speakersListWidget.currentItem().text()
        ampli = self.amplisListWidget.currentItem().text()
        impedanceMode = self.impedanceListWidget.currentItem().text()
        impedanceInt = int(
            self.impedanceListWidget.currentItem().text().replace(" (bridge)", "")
        )

        # Get values
        speakerBaffle = self.speakers[spk].baffle
        speakerPower = int(
            self.speakers[spk].power * (self.speakers[spk].impedance / impedanceInt)
        )
        ampliGain = self.amplis[ampli].gain
        ampliPower = self.amplis[ampli].power.get(impedanceMode)

        # Update value labels, set empty string if not possible
        self.impedanceValue.setText(f"{impedanceInt}")
        self.speakerBaffleValue.setCurrentText(f"{speakerBaffle}")
        self.ampliGainValue.setText(f"{ampliGain}")
        # Example: F221 cannot be 8 Ohm
        self.speakerPowerValue.setText(
            f"{speakerPower if impedanceInt <= self.speakers[spk].impedance else ''}"
        )
        # Example: MA6.8Q does not support 2 Ohm
        self.ampliPowerValue.setText(f"{ampliPower if ampliPower else ''}")

        # Update selected labels
        self.selectedSpeakerLabel.setText(f"[{spk}]")
        self.selectedAmpliLabel.setText(f"[{ampli}]")

        # Check if configuration is possible, if not then switch to custom
        if not self.ampliPowerValue.text():
            self.selectedAmpliLabel.setText(self.customText)
        if not self.speakerPowerValue.text():
            self.selectedSpeakerLabel.setText(self.customText)

    def _updateOnInputsSpeaker(self) -> None:
        """Update selected speaker to custom and update threshold."""

        self.selectedSpeakerLabel.setText(self.customText)
        self._updatethreshold()

    def _updateOnInputsAmpli(self) -> None:
        """Update selected ampli to custom and update threshold."""

        self.selectedAmpliLabel.setText(self.customText)
        self._updatethreshold()

    def _updatethreshold(self) -> None:
        """Update threshold result with current parameters."""

        if not (
            self.impedanceValue.text()
            and self.speakerBaffleValue.currentText()
            and self.speakerPowerValue.text()
            and self.ampliGainValue.text()
            and self.ampliPowerValue.text()
        ):
            self.thresholdValue.setText("")
            return

        limit = Limiter(
            int(self.impedanceValue.text()),
            self.speakerBaffleValue.currentText(),
            int(self.speakerPowerValue.text()),
            float(self.ampliGainValue.text()),
            int(self.ampliPowerValue.text()),
        )

        smartSpkMax, smartAmpMax, smartThreshold = limit.computeTreshold(smartLimit=True)
        trueSpkMax, trueAmpMax, trueThreshold = limit.computeTreshold(smartLimit=False)

        self.thresholdValue.setText(f"{smartThreshold}")
        self.thresholdValue.setToolTip(
            f"smart limit = {smartThreshold} dBu\n"
            + f"smart speaker Vmax = {smartSpkMax} V\n"
            + f"smart ampli Vmax = {smartAmpMax} V\n"
            + "---------------------------------\n"
            + f"true limit = {trueThreshold} dBu\n"
            + f"true speaker Vmax = {trueSpkMax} V\n"
            + f"true ampli Vmax = {trueAmpMax} V"
        )


def run() -> None:
    app = QApplication()
    app.setStyleSheet(qdarktheme.load_stylesheet())
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
