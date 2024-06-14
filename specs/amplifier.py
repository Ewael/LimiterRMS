class Amplifier:
    def __init__(self, reference: str, gain: float, power: dict[int, int | None], outputs: int | None) -> None:
        """Init all attributes.

        If one value is None then it means info is missing.
        This can only be true for power and ouputs.

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
