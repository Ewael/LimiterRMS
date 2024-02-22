from math import *
from decimal import Decimal, ROUND_DOWN, ROUND_UP


class Speaker:
    def __init__(self, _name: str, _power: int, _impedance: int, _baffle: int) -> None:
        self.name = _name
        self.power = _power
        self.impedance = _impedance
        self.baffle = _baffle

class Amplifier:
    def __init__(self, _name: str, _power: dict, _gain: int) -> None:
        self.name = _name
        self.power = _power
        self.gain = _gain


SEALED = 0
OPEN = 1

speakers = {
    "MTH": Speaker(_name="MTH", _power=1500, _impedance=8, _baffle=SEALED),
    "F221": Speaker(_name="F221", _power=2000, _impedance=4, _baffle=SEALED),
    "MKH": Speaker(_name="MKH", _power=900, _impedance=4, _baffle=SEALED),
    "BPH": Speaker(_name="BPH", _power=1000, _impedance=4, _baffle=SEALED),
    "NEXOK": Speaker(_name="NEXOK", _power=600, _impedance=4, _baffle=OPEN),
    "NEXOM": Speaker(_name="NEXOM", _power=350, _impedance=8, _baffle=SEALED),
    "NEXOH": Speaker(_name="NEXOH", _power=150, _impedance=8, _baffle=SEALED),
    "ERICS": Speaker(_name="ERICS", _power=1000, _impedance=4, _baffle=OPEN),
    "ERICL": Speaker(_name="ERICL", _power=500, _impedance=8, _baffle=OPEN),
    "ERICM": Speaker(_name="ERICM", _power=400, _impedance=8, _baffle=SEALED),
    "ERICH": Speaker(_name="ERICH", _power=320, _impedance=8, _baffle=SEALED),
    "ORPH": Speaker(_name="ORPH", _power=700, _impedance=8, _baffle=SEALED),
    "MINI-ORPH": Speaker(_name="MINI-ORPH", _power=300, _impedance=8, _baffle=SEALED),
    "TMS3L": Speaker(_name="TMS3L", _power=500, _impedance=4, _baffle=SEALED),
    "TMS3M": Speaker(_name="TMS3M", _power=200, _impedance=8, _baffle=SEALED),
    "TMS3H": Speaker(_name="TMS3H", _power=75, _impedance=8, _baffle=SEALED),
}
amplis = {
    "TSA": Amplifier(_name="TSA", _power={"4": 1670, "8": 1220}, _gain=37.8),
    "TPA": Amplifier(_name="TPA", _power={"4": 4400, "8": 2350}, _gain=35),
    "9001": Amplifier(_name="9001", _power={"4": 2050, "8": 1100}, _gain=40),
    "LA": Amplifier(_name="LA", _power={"4": 1500, "8": 1100}, _gain=32),
    "HPA": Amplifier(_name="HPA", _power={"4": 1800, "8": 1100}, _gain=36),
}


def limit(spk: Speaker, amp: Amplifier, impedance: int, sensitivity: float=0.775) -> float:
    """Compute threshold for given speaker, amplifier and impedance for 0.775V sensitivity
    """

    if not amp.power.get(str(impedance)):
        raise ValueError("f{amp.name} does not support {spk.impedance} Ohm")
    if impedance > spk.impedance: # example: F221 cannot be 8 Ohm
        raise ValueError("f{spk.name} impedance cannot be higher than {spk.impedance} Ohm")

    # update power values that we will use depending on current impedance
    spk_power = spk.power * (spk.impedance / impedance)
    amp_power = amp.power[str(impedance)]

    lim_spk = 20 * log10(sqrt((spk_power / (1.5625 if spk.baffle == OPEN else 2.34375)) * impedance) / sensitivity) - amp.gain
    lim_amp = 20 * log10(sqrt((amp_power / 2) * impedance) / sensitivity) - amp.gain
    lim = min(lim_spk, lim_amp)
    lim_dbU = Decimal(lim).quantize(Decimal('.1'), rounding=(ROUND_DOWN if lim > 0 else ROUND_UP))

    return lim_dbU


def main():
    # on demande quelle enceinte, quel ampli et quelle impédance
    # on initialise spk et amp en leur donnant ref + impédance
    # on envoie les deux objets à calc
    for spk in speakers:
        print(limit(speakers[spk], amplis["TSA"], 4))


if __name__ == '__main__':
    main()