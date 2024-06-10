import sys

from decimal import Decimal, ROUND_DOWN, ROUND_UP
from pandas import read_excel
from math import log10, sqrt
from pathlib import Path

from PySide6.QtWidgets import QListWidget, QListWidgetItem, QApplication, QHBoxLayout, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt


APP_NAME = "LimiterRMS"
INVENTORY_NAME = r"inventory.xlsx"
INVENTORY_PATH = str(Path(__file__).parent.resolve()) + "\\" + INVENTORY_NAME


class Speaker:
    def __init__(self, name: str, reference: str, impedance: int, power: int, response: str, baffle: str) -> None:
        self.name = name
        self.reference = reference
        self.impedance = impedance
        self.power = power
        self.response = response
        self.baffle = baffle


class Amplifier:
    def __init__(self, name: str, reference: str, gain: int, power: dict, outputs: int) -> None:
        self.name = name
        self.reference = reference
        self.gain = gain
        self.power = power
        self.outputs = outputs


def getSpecs(path: str) -> tuple[dict[str, Amplifier], dict[str, Speaker]]:
    """Return list of speakers & amplifiers specs from inventory"""

    data_amp = read_excel(
        path,
        sheet_name="amplifiers",
        dtype={
            "name": str,
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
        dtype={"name": str, "reference": str, "impedance": int, "power": int, "response": str, "baffle": str},
    ).to_dict(orient="records")

    amplis, speakers = {}, {}
    for amp in data_amp:
        amplis[amp["name"]] = Amplifier(
            name=amp["name"],
            reference=amp["reference"],
            gain=amp["gain"],
            power={8: amp["power_8ohm"], 4: amp["power_4ohm"], 2: amp["power_2ohm"]},
            outputs=amp["outputs"],
        )
    for spk in data_spk:
        speakers[spk["name"]] = Speaker(
            name=spk["name"],
            reference=spk["reference"],
            impedance=spk["impedance"],
            power=spk["power"],
            response=spk["response"],
            baffle=spk["baffle"],
        )

    return amplis, speakers


def limit(spk: Speaker, amp: Amplifier, impedance: int, sensitivity: float = 0.775) -> Decimal:
    """Compute threshold for given speaker, amplifier and impedance for 0.775V sensitivity"""

    if not amp.power.get(impedance):
        raise ValueError("f{amp.name} does not support {spk.impedance} Ohm")
    if impedance > spk.impedance:  # Example: F221 cannot be 8 Ohm
        raise ValueError("f{spk.name} impedance cannot be higher than {spk.impedance} Ohm")

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
    selectedAmpli = None
    selectedSpeaker = None
    selectedImpedance = None
    result = "0"

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.setGeometry(600, 300, 800, 500)

        # Get amplis and speakers data
        amplis, speakers = getSpecs(INVENTORY_PATH)

        # Amp, speaker and impedance row
        amplisListWidget = QListWidget()
        for ampli in amplis:
            amplisListWidget.addItem(QListWidgetItem(self.tr(ampli)))
        amplisListWidget.setMinimumWidth(2 * amplisListWidget.sizeHintForColumn(0) + amplisListWidget.frameWidth())
        amplisListWidget.setMinimumHeight(
            amplisListWidget.sizeHintForRow(0) * amplisListWidget.count() + 2 * amplisListWidget.frameWidth()
        )
        speakersListWidget = QListWidget()
        for speaker in speakers:
            speakersListWidget.addItem(QListWidgetItem(self.tr(speaker)))
        speakersListWidget.setMinimumWidth(
            2 * speakersListWidget.sizeHintForColumn(0) + speakersListWidget.frameWidth()
        )
        speakersListWidget.setMinimumHeight(
            speakersListWidget.sizeHintForRow(0) * speakersListWidget.count() + 2 * speakersListWidget.frameWidth()
        )
        impedanceListWidget = QListWidget()
        for impedance in [2, 4, 8]:
            impedanceListWidget.addItem(QListWidgetItem(self.tr(str(impedance))))
        impedanceListWidget.setMinimumWidth(
            2 * impedanceListWidget.sizeHintForColumn(0) + impedanceListWidget.frameWidth()
        )
        impedanceListWidget.setMinimumHeight(
            impedanceListWidget.sizeHintForRow(0) * impedanceListWidget.count() + 2 * impedanceListWidget.frameWidth()
        )
        selectionRow = QHBoxLayout()
        selectionRow.addWidget(amplisListWidget)
        selectionRow.addWidget(speakersListWidget)
        selectionRow.addWidget(impedanceListWidget)

        # Compute row
        computeButton = QPushButton("Compute RMS Limiter")
        computeButton.clicked.connect(self._updateLimit)

        # Result row
        self.resultLabel = QLabel("allo")

        # Main layout
        mainLayout = QVBoxLayout(self)
        mainLayout.addLayout(selectionRow)
        mainLayout.addWidget(computeButton, alignment=Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(self.resultLabel, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(mainLayout)

        # On initialise spk et amp en leur donnant ref + impédance
        # On envoie les deux objets à calc

        self.show()

    def _updateLimit(self):
        print("Hi!")


def run() -> None:
    app = QApplication()
    window = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
