from classes.Limb import Limb, LimbName
from classes.Person import Person
from classes.Route import Route
from classes.ImageAttribute import ImageAttribute
from copy import copy


class State:
    def __init__(
        self,
        lf: Limb,
        rf: Limb,
        lh: Limb,
        rh: Limb,
        person: Person,
        route: Route,
        image_attributes: ImageAttribute,
    ):
        self.lf, self.rf, self.lh, self.rh = lf, rf, lh, rh
        self.person = person
        self.moves = []
        self.costs = []
        self.route = route
        self.wall_height_inches = (
            180  # Represents real height of wall <- need to measure
        )
        self.image_attributes = image_attributes
        self.wall_height_pixels = (
            self.image_attributes.height
        )  # placeholder <- Need to extract from image

    # Not sure where to put this
    def inches_to_pixels(self, inches: int):
        return (self.wall_height_pixels / self.wall_height_inches) * inches

    def __eq__(self, other):
        return (
            self.lf.hold == other.lf.hold
            and self.rf.hold == other.rf.hold
            and self.rh.hold == other.rh.hold
            and self.lh.hold == other.lh.hold
        ) or (
            self.lf.hold == other.rf.hold
            and self.rf.hold == other.lf.hold
            and self.rh.hold == other.lh.hold
            and self.lh.hold == other.rh.hold
        )

    def __repr__(self):
        return f"{self.moves}"

    def get_successors(self):
        succs = []
        limbs = [self.lf, self.rf, self.lh, self.rh]
        for i in range(len(limbs)):
            neighs = self.get_neighbors(limbs[i])
            for neigh in neighs:
                # print("Hi neighbor")
                new_state = copy(self)
                if i == 0:
                    new_state.lf = Limb(LimbName.LEFT_LEG, 2.5, 8, neigh)
                    action = (self.lf, neigh)
                if i == 1:
                    new_state.rf = Limb(LimbName.RIGHT_LEG, 2.5, 8, neigh)
                    action = (self.rf, neigh)
                if i == 2:
                    new_state.lh = Limb(LimbName.LEFT_HAND, 8, 2, neigh)
                    action = (self.lh, neigh)
                if i == 3:
                    new_state.rh = Limb(LimbName.RIGHT_HAND, 8, 2, neigh)
                    action = (self.rh, neigh)
                succs.append((new_state, action))
        # print(succs)
        return succs

    def get_neighbors(self, limb):
        neighbors = []
        for hold in self.route.holds:
            if not hold == limb.hold:
                if limb.name in [LimbName.LEFT_LEG, LimbName.RIGHT_LEG]:
                    low_arm = max([self.lh.hold.y, self.rh.hold.y])
                    if (
                        0
                        < limb.hold.y - hold.y
                        < self.inches_to_pixels(self.person.leg_length)
                        and abs(hold.x - limb.hold.x)
                        < self.inches_to_pixels(self.person.leg_length)
                        and hold.y > low_arm
                    ):
                        neighbors.append(hold)
                elif limb.name in [LimbName.LEFT_HAND, LimbName.RIGHT_HAND]:
                    # print("Checking arm neighbors")
                    # print("HAND TIME 1")
                    upper_leg, lower_leg = sorted([self.lf.hold.y, self.rf.hold.y])
                    if (
                        abs(hold.x - limb.hold.x)
                        < self.inches_to_pixels(self.person.wingspan)
                        and lower_leg - hold.y
                        < self.inches_to_pixels(self.person.height * 0.8)
                        and hold.y < upper_leg
                        and 0 < limb.hold.y - hold.y
                    ):
                        neighbors.append(hold)
        return neighbors
