from decimal import Decimal, ROUND_DOWN, ROUND_UP
from math import log10, sqrt


class Limiter:
    # El famoso "smart limiter" from Hornplans
    baffleFactorOpen = 1.5625
    baffleFactorClosed = 2.34375
    ampliFactor = 2

    def __init__(
        self,
        impedance: float,
        speakerBaffle: str,
        speakerPower: int,
        ampliGain: float,
        ampliPower: int,
        sensitivity: float = 0.775,
    ) -> None:
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

    def computeTreshold(self, smartLimit: bool) -> tuple[Decimal, Decimal, Decimal]:
        """Compute threshold for given speaker, amplifier and impedance at 0.775V sensitivity.

        Parameters:
            smartLimit: Compute threshold with strict factor on power values
        """

        baffleFactor = (
            1
            if not smartLimit
            else (
                self.baffleFactorOpen
                if self.speakerBaffle == "OPEN"
                else self.baffleFactorClosed
            )
        )
        ampliFactor = 1 if not smartLimit else self.ampliFactor

        """
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

        # RMS voltage corresponding to given speaker power at given impedance
        V_spk_max = sqrt((self.speakerPower / baffleFactor) * self.impedance)
        # We convert this RMS voltage to dBu at 0.775V sensitivity
        dBu_spk_max = 20 * log10(V_spk_max / self.sensitivity)
        # Then we remove gain of the amplifier
        threshold_spk = dBu_spk_max - self.ampliGain

        # RMS voltage corresponding to given amplifier power at given impedance
        V_amp_max = sqrt((self.ampliPower / ampliFactor) * self.impedance)
        # RMS to dBu conversion
        dBu_amp_max = 20 * log10(V_amp_max / self.sensitivity)
        # Gain substraction
        threshold_amp = dBu_amp_max - self.ampliGain

        # We take the most strict threshold to protect ampli & speaker
        threshold = min(threshold_spk, threshold_amp)
        threshold = Decimal(threshold).quantize(
            Decimal(".1"), rounding=(ROUND_DOWN if threshold > 0 else ROUND_UP)
        )

        return (
            Decimal(V_spk_max).quantize(Decimal(".01")),
            Decimal(V_amp_max).quantize(Decimal(".01")),
            threshold,
        )
