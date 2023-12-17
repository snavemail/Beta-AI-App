from enum import Enum
from classes.Hold import Hold


class LimbName(Enum):
    """
    Class for limb names
    """

    LEFT_HAND = "Left Hand"
    RIGHT_HAND = "Right Hand"
    LEFT_LEG = "Left Leg"
    RIGHT_LEG = "Right Leg"


class Limb:
    def __init__(self, name: LimbName, strength: int, flexibility: int, hold: Hold):
        self.name, self.strength, self.flexibility, self.hold = (
            name,
            strength,
            flexibility,
            hold,
        )

    def __repr__(self):
        return f"{self.name} at {self.hold}"
