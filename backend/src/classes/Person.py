class Person:
    def __init__(self, height: int) -> None:
        """
        Represents a person class to get their
        height: height in inches rounded to nearest whole number
        """
        self.height = height
        self.wingspan = height * 1.06
        self.reach = height * 1.35
        self.leg_length = height * 0.5
