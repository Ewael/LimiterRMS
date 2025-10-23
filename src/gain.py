from decimal import Decimal
from math import log10, sqrt

class AmplifierGain(float):
    def __init__(self, voltageIn: float, voltageOut:float) -> None:
        """Initiate all attributes.
        
        Parameters:
            voltageIn: Voltage between pin 2 and 3 of in XLR going in the amp
            voltageOut: Voltage between + and - of the amplified signal going out of the amp
        """

        self.voltageIn = voltageIn
        self.voltageOut = voltageOut
        
    def computeGain(self) -> Decimal:
        """
        """
        
        return 0