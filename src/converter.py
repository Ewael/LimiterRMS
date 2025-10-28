from decimal import Decimal
from math import sqrt


def freqToDistance(freq: int, c: float) -> Decimal:
    """Return wave length (m) from given freq (Hz) and c (m.s-1)."""

    distance = c / freq
    return Decimal(distance).quantize(Decimal(".01"))


def freqToTime(freq: int, c: float) -> Decimal:
    """Return period (ms) from given freq (Hs)."""

    time = 1 / (freq * 0.001)
    return Decimal(time).quantize(Decimal(".001"))


def distanceToTime(distance: float, c: float) -> Decimal:
    """Return time (ms) from given d and c."""

    time = (distance / c) * 1000  # time (ms)
    return Decimal(time).quantize(Decimal(".001"))


def distanceToFreq(distance: float, c: float) -> Decimal:
    """ "Return freq (Hz) from given distance (m) and c (m.s-1)."""

    freq = c / distance
    return Decimal(freq).quantize(Decimal(".01"))


def timeToFreq(time: float) -> Decimal:
    """Return freq (Hz) from given time (ms)."""

    freq = 1 / (time * 0.001)
    return Decimal(freq).quantize(Decimal(".01"))


def timeToDistance(time: float, c: float) -> Decimal:
    """Return distance (m) from given time (ms)."""

    distance = (time * c) / 1000
    return Decimal(distance).quantize(Decimal(".01"))


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
