from pathlib import Path
from pandas import read_excel
from math import log10, sqrt
from decimal import Decimal, ROUND_DOWN, ROUND_UP


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


def getSpecs(path: str) -> tuple[list[Speaker], list[Amplifier]]:
    """Return list of speakers & amplifiers specs from inventory
    """

    data_amp = read_excel(
        path,
        sheet_name="amplifiers",
        dtype={
            "name": str,
            "reference": str,
            "gain": float,
            #"power_8ohm": int,
            #"power_4ohm": int,
            #"power_2ohm": int,
            #"outputs": int
            }
        ).to_dict(orient="records")
    data_spk = read_excel(
        path,
        sheet_name="speakers",
        dtype={
            "name": str,
            "reference": str,
            "impedance": int,
            "power": int,
            "response": str,
            "baffle": str
            }
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


def limit(spk: Speaker, amp: Amplifier, impedance: int, sensitivity: float=0.775) -> float:
    """Compute threshold for given speaker, amplifier and impedance for 0.775V sensitivity
    """

    if not amp.power.get(impedance):
        raise ValueError("f{amp.name} does not support {spk.impedance} Ohm")
    if impedance > spk.impedance: # example: F221 cannot be 8 Ohm
        raise ValueError("f{spk.name} impedance cannot be higher than {spk.impedance} Ohm")

    # update power values that we will use depending on current impedance
    spk_power = spk.power * (spk.impedance / impedance)
    amp_power = amp.power[impedance]

    lim_spk = 20 * log10(sqrt((spk_power / (1.5625 if spk.baffle == "OPEN" else 2.34375)) * impedance) / sensitivity) - amp.gain
    lim_amp = 20 * log10(sqrt((amp_power / 2) * impedance) / sensitivity) - amp.gain
    lim = min(lim_spk, lim_amp)
    lim_dbU = Decimal(lim).quantize(Decimal('.1'), rounding=(ROUND_DOWN if lim > 0 else ROUND_UP))

    return lim_dbU


def main():
    # on récupère les données des amplis & enceintes
    amplis, speakers = getSpecs(INVENTORY_PATH)

    # on demande quelle enceinte, quel ampli et quelle impédance
    # on initialise spk et amp en leur donnant ref + impédance
    # on envoie les deux objets à calc
    for spk in speakers:
        print(limit(speakers[spk], amplis["TPA"], 4))


if __name__ == '__main__':
    main()