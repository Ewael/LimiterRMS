from decimal import Decimal, ROUND_DOWN, ROUND_UP
from math import log10, sqrt


class Limiter:
    def __init__(
        self,
        impedance: float,
        speakerBaffle: str,
        speakerPower: int,
        ampliGain: float,
        ampliPower: int,
        sensitivity: float = 0.775,
    ):
        """Initiate all attributes.

        Paramters:
            impedance: Working impedance
            speakerBaffle: Type of baffle, either "OPEN" or "CLOSED"
            speakerPower: AES speaker power
            ampliGain: Ampli gain in dBu
            ampliPower: RMS ampli power
            sensitivity: Sensitivity, defaults to 0.775V
        """

        self.impedance = impedance
        self.speakerBaffle = speakerBaffle
        self.speakerPower = speakerPower
        self.ampliGain = ampliGain
        self.ampliPower = ampliPower
        self.sensitivity = sensitivity

    def computeTreshold(self) -> Decimal:
        """Compute threshold for given speaker, amplifier and impedance at 0.775V sensitivity.

        Dans un ampli,

            P = U ^ 2 / R
        <=> U = sqrt( P * R )

            U_out = U_in * 10 ^ ( gain_dB / 20 )
        <=> U_in = U_out / 10 ^ ( gain_dB / 20 )

        Or,

            dBu = 20 * log10( U / 0.775 )

        Donc, on a

            dBu_in = 20 * log10( U_out / 0.775 ) - gain_dB
        """

        # El famoso "smart limiter" from Hornplans
        baffleFactor = 1.5625 if self.speakerBaffle == "OPEN" else 2.34375
        # RMS voltage corresponding to given speaker power at given impedance
        V_spk = sqrt((self.speakerPower / baffleFactor) * self.impedance)
        # We convert this RMS voltage to dBu at 0.775V sensitivity
        dBu_spk = 20 * log10(V_spk / self.sensitivity)
        # Then we remove gain of the amplifier
        threshold_spk = dBu_spk - self.ampliGain

        # We do the same with amplifier power, factor is from Hornplans again
        ampliFactor = 2
        # RMS voltage corresponding to given amplifier power at given impedance
        V_amp = sqrt((self.ampliPower / ampliFactor) * self.impedance)
        # RMS to dBu conversion
        dBu_amp = 20 * log10(V_amp / self.sensitivity)
        # Gain substraction
        threshold_amp = dBu_amp - self.ampliGain

        # We take the most strict threshold to protect ampli & speaker
        threshold = min(threshold_spk, threshold_amp)
        threshold = Decimal(threshold).quantize(
            Decimal(".1"), rounding=(ROUND_DOWN if threshold > 0 else ROUND_UP)
        )

        return threshold
