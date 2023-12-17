class Hold:
    """
    Represents a hold in the route
    Has an x,y coordinate, a difficulty rating obtained from the model, a width and height, and an angle obtained from another model.
    """

    def __init__(
        self, x: int, y: int, diff: float, width: float, height: float, angle: int
    ):
        # Coords = middle of the bounding box
        self.x = x
        self.y = y
        self.diff = diff
        self.width = width
        self.height = height
        self.angle = angle

    def get_top_left(self):
        return (self.coords[0] - self.width / 2, self.coords[1] - self.height / 2)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __gt__(self, other):
        return self.y > other.y

    def __lt__(self, other):
        return self.y < other.y

    def __ge__(self, other):
        return self.y >= other.y

    def __le__(self, other):
        return self.y <= other.y

    def __repr__(self):
        return f"""Hold: Top left at {self.x}, {self.y}
                Width = {self.width}, Height = {self.height}
                Difficulty = {round(self.diff, 2)}/10, Angle = {self.angle} degrees\n"""
