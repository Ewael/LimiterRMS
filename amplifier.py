class Amplifier:
    def __init__(self, reference: str, gain: int, power: dict, outputs: int) -> None:
        """Init all attributes.

        Parameters:
            reference: Ampli complete reference, for instance "t.amp TSA 4-1300"
            gain: Ampli gain, see its documentation
            power: Ampli power, with following structure:
                {
                    8: 8 Ohm power
                    4: 4 Ohm power
                    2: 2 Ohm power
                }
            outputs: Number of outputs
        """

        self.reference = reference
        self.gain = gain
        self.power = power
        self.outputs = outputs
