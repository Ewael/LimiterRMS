class Speaker:
    def __init__(self, reference: str, impedance: int, power: int, response: str, baffle: str) -> None:
        """Init all attributes.

        Parameters:
            reference: Speaker complete reference, for instance "MTH 4654 (RCF LF18X401)"
            impedance: Speaker impedance, see its documentation
            power: Speaker power in Watt AES
            response: Speaker range of usage in Hz, for instance "330-2.2k"
            baffle: Baffle type, either "OPEN" or "CLOSED"
        """

        self.reference = reference
        self.impedance = impedance
        self.power = power
        self.response = response
        self.baffle = baffle
