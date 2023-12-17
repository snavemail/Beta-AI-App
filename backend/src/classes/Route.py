from classes.Hold import Hold


class Route:
    def __init__(self, holds: Hold, start1: Hold, start2: Hold, finish: Hold):
        self.holds = holds
        self.start_hold1 = start1
        self.start_hold2 = start2
        self.finish_hold = finish
