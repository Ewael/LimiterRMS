from decimal import Decimal
from math import sqrt


def freqToDistance(freq: float, c: float) -> Decimal:
    """Return wave length (m) from given freq and c."""

    distance = c / freq
    return Decimal(distance).quantize(".01")


def distanceToTime(distance: float, c: float) -> Decimal:
    """Return time (ms) from given d and c."""

    time = distance / c
    return Decimal(time).quantize(".001")


def timeToFreq(time: float) -> int:
    """Return freq (Hz) from given time."""

    freq = 1 / time
    return int(freq)


def computeC(temperature: float) -> int:
    """Return speed of sound in air at given temperature."""

    # NASA WAY
    """
    g = 1.4  # gamma is adiabatic index of air
    R = 286  # molar gas constant (m2/s2/K0)
    T = 273.15 + temperature  # absolute temperature (K)
    return Decimal(sqrt(g * R * T)).quantize(Decimal(".01"))
    """

    # Wikipedia way
    return int(331.3 + temperature * 0.606)
