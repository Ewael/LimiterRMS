from decimal import Decimal
from math import log10


class AmpGain:
    def __init__(self, voltageIn: float, voltageOut: float) -> None:
        """Initiate all attributes.

        Parameters:
            voltageIn: Voltage between pin 2 and 3 of in XLR going in the amp
            voltageOut: Voltage between + and - of the amplified signal going out of the amp
        """

        self.voltageIn = voltageIn
        self.voltageOut = voltageOut

    def computeAmpGain(self) -> Decimal:
        """Return amplifier gain from V_IN and V_OUT.

        U_out = U_in * 10^( gain / 20 )
        <=> gain = 20 * log10( U_out / U_in )
        """

        ampGain = 20 * log10(self.voltageOut / self.voltageIn)
        return Decimal(ampGain).quantize(Decimal(".01"))
