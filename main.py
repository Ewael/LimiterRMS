import sys

from decimal import Decimal, ROUND_DOWN, ROUND_UP
from pandas import read_excel
from math import log10, sqrt, isnan
from pathlib import Path

from PySide6.QtWidgets import (
    QListWidget,
    QListWidgetItem,
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PySide6.QtCore import Qt

from amplifier import Amplifier
from speaker import Speaker


OHM = "\u2126"
APP_NAME = "LimiterRMS"
INVENTORY_NAME = r"inventory.xlsx"
INVENTORY_PATH = str(Path(__file__).parent.resolve()) + "\\" + INVENTORY_NAME


def getSpecs(path: str) -> tuple[dict[str, Amplifier], dict[str, Speaker]]:
    """Return list of speakers & amplifiers specs from inventory."""

    data_amp = read_excel(
        path,
        sheet_name="amplifiers",
        # We can not precise type for optionnal columns
        dtype={
            "reference": str,
            "gain": float,
            # "power_8ohm": int,
            # "power_4ohm": int,
            # "power_2ohm": int,
            # "outputs": int,
        },
    ).to_dict(orient="records")
    data_spk = read_excel(
        path,
        sheet_name="speakers",
        dtype={
            "reference": str,
            "impedance": int,
            "power": int,
            "response": str,
            "baffle": str,
        },
    ).to_dict(orient="records")

    amplis, speakers = {}, {}
    for amp in data_amp:
        amplis[amp["reference"]] = Amplifier(
            reference=amp["reference"],
            gain=amp["gain"],
            power={
                8: int(amp["power_8ohm"]) if not isnan(amp["power_8ohm"]) else None,
                4: int(amp["power_4ohm"]) if not isnan(amp["power_4ohm"]) else None,
                2: int(amp["power_2ohm"]) if not isnan(amp["power_2ohm"]) else None,
            },
            outputs=int(amp["outputs"]) if not isnan(amp["outputs"]) else None,
        )
    for spk in data_spk:
        speakers[spk["reference"]] = Speaker(
            reference=spk["reference"],
            impedance=spk["impedance"],
            power=spk["power"],
            response=spk["response"],
            baffle=spk["baffle"],
        )

    return amplis, speakers


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
        self.amplis, self.speakers = getSpecs(INVENTORY_PATH)

        # Ampli row
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

        # Speaker row
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

        # Impedance row
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

        # Selection layout
        selectionLayout = QHBoxLayout()
        selectionLayout.addWidget(self.amplisListWidget)
        selectionLayout.addWidget(self.speakersListWidget)
        selectionLayout.addWidget(self.impedanceListWidget)

        # Left of recap layout are text labels
        self.impedanceText = QLabel("Impedance:")
        self.speakerPowerText = QLabel("Speaker power:")
        self.ampliPowerText = QLabel("Ampli power:")
        self.ampliGainText = QLabel("Ampli gain:")
        self.tresholdText = QLabel("Treshold:")
        self.tresholdText.setStyleSheet("color: red")

        # Text layout
        recapKeyLayout = QVBoxLayout()
        recapKeyLayout.addWidget(self.impedanceText, alignment=Qt.AlignmentFlag.AlignRight)
        recapKeyLayout.addWidget(self.speakerPowerText, alignment=Qt.AlignmentFlag.AlignRight)
        recapKeyLayout.addWidget(self.ampliPowerText, alignment=Qt.AlignmentFlag.AlignRight)
        recapKeyLayout.addWidget(self.ampliGainText, alignment=Qt.AlignmentFlag.AlignRight)
        recapKeyLayout.addWidget(self.tresholdText, alignment=Qt.AlignmentFlag.AlignRight)

        # Right of recap layout are value labels, those will update on user choices in lists
        self.impedanceValue = QLabel()
        self.speakerPowerValue = QLabel()
        self.ampliPowerValue = QLabel()
        self.ampliGainValue = QLabel()
        self.tresholdValue = QLabel()
        self.tresholdValue.setStyleSheet("color: red")

        # Values layout
        recapValuesLayout = QVBoxLayout()
        recapValuesLayout.addWidget(self.impedanceValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapValuesLayout.addWidget(self.speakerPowerValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapValuesLayout.addWidget(self.ampliPowerValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapValuesLayout.addWidget(self.ampliGainValue, alignment=Qt.AlignmentFlag.AlignLeft)
        recapValuesLayout.addWidget(self.tresholdValue, alignment=Qt.AlignmentFlag.AlignLeft)

        # Connections with labels and set default values at start
        self.amplisListWidget.itemSelectionChanged.connect(self._updateValues)
        self.speakersListWidget.itemSelectionChanged.connect(self._updateValues)
        self.impedanceListWidget.itemSelectionChanged.connect(self._updateValues)
        self._updateValues()

        # Recap layout
        recapLayout = QHBoxLayout()
        recapLayout.addLayout(recapKeyLayout)
        recapLayout.addLayout(recapValuesLayout)

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
        """Update limiter value."""

        # Get selected speaker, ampli and impedance
        spk = self.speakersListWidget.currentItem().text()
        ampli = self.amplisListWidget.currentItem().text()
        impedance = int(self.impedanceListWidget.currentItem().text())

        # Check if we can really compute treshold
        if not self.amplis[ampli].power.get(impedance):  # Example: MA6.8Q does not support 2 Ohm
            self.ampliPowerValue.setText(f"{self.amplis[ampli].reference} does not support {impedance} {OHM}")
            self.tresholdValue.setText("Can't compute treshold")
            return
        if impedance > self.speakers[spk].impedance:  # Example: F221 cannot be 8 Ohm
            self.speakerPowerValue.setText(
                f"{self.speakers[spk].reference} impedance cannot be higher than {self.speakers[spk].impedance} {OHM}"
            )

            self.tresholdValue.setText("Can't compute treshold")
            return

        # Get values and compute treshold
        speakerPower = int(self.speakers[spk].power * (self.speakers[spk].impedance / impedance))
        ampliPower = self.amplis[ampli].power[impedance]
        ampliGain = self.amplis[ampli].gain
        treshold = limit(self.speakers[spk], self.amplis[ampli], impedance)

        # Update labels
        self.impedanceValue.setText(f"{impedance} {OHM}")
        self.speakerPowerValue.setText(f"{speakerPower} Watts AES (for {impedance} {OHM})")
        self.ampliPowerValue.setText(f"{ampliPower} Watts RMS (for {impedance} {OHM})")
        self.ampliGainValue.setText(f"{ampliGain} dB")
        self.tresholdValue.setText(f"{treshold} dBu")


def run() -> None:
    app = QApplication()
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
