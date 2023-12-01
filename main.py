from enum import Enum

class RockWall:
  def __init__(self, boulders: list, angle):
    """
    Initialize a RockWall object.

    Args:
      boulders (list): A list of Boulder objects.
      angle (int): The angle of the wall in degrees 0-360, where 0 is up, positive is overhang, and negative is slab.

    """
    self.boulders = boulders
    self.angle = angle


class BoulderType(Enum):
  JUG = 1
  SLOPER = 2
  FOOTHOLD = 3
  CRIMP = 4
  PINCH = 5
  POCKET = 6
  VOLUME = 7


class Boulder:
  def __init__(self, boulder_type, orientation, size, color, x_coord, y_coord, start, finish):
    """
    Initialize a Boulder object.

    Args:
      boulder_type: The BoulderType object representing the type of the boulder.
      orientation: The orientation of the boulder in degrees -180 to 180, where 0 is up, 90 is right, -90 is left, and +-180 is down.
      size: The size of the boulder in pixels?
      color: The color of the boulder. Taken from the machine learning classifier
      x_coord: The x-coordinate of the bottom left of the boulder.
      y_coord: The y-coordinate of the bottom left of the boulder.

    """
    self.boulder_type = boulder_type
    self.orientation = orientation
    self.size = size
    self.color = color
    self.x_coord = x_coord
    self.y_coord = y_coord
    self.start = start
    self.finish = finish



foothold1 = Boulder(BoulderType.FOOTHOLD, -10, 1, "red", 2.5, 1, False, False)
foothold2 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 3.5, 3, False, False)
foothold3 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 2.5, 5, False, False)
foothold4 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 6, 8, False, False)
foothold5 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 6, 10, False, False)
foothold6 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 8, 12, False, False)
foothold7 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 9, 13, False, False)
foothold8 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 10, 14, False, False)
foothold9 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 10, 18, False, False)
foothold10 = Boulder(BoulderType.FOOTHOLD, 0, 1, "red", 10, 23, False, False)

jug1 = Boulder(BoulderType.JUG, 0, 10, "red", 2, 12, True, False)
jug2 = Boulder(BoulderType.JUG, 0, 10, "red", 8, 40, False, True)

pinch1 = Boulder(BoulderType.PINCH, 0, 10, "red", 3, 16, False, False)
pinch2 = Boulder(BoulderType.PINCH, 0, 10, "red", 4, 17, False, False)
pinch3 = Boulder(BoulderType.PINCH, 0, 10, "red", 4, 19, False, False)
pinch4 = Boulder(BoulderType.PINCH, 45, 10, "red", 7, 22, False, False)
pinch5 = Boulder(BoulderType.PINCH, 50, 10, "red", 7, 23, False, False)
pinch6 = Boulder(BoulderType.PINCH, -5, 10, "red", 9, 28, False, False)
pinch7 = Boulder(BoulderType.PINCH, -30, 10, "red", 8, 36, False, False)
pinch8 = Boulder(BoulderType.PINCH, 0, 10, "red", 10, 38, False, False)

boulders = [
  foothold1,
  foothold2,
  foothold3,
  foothold4,
  foothold5,
  foothold6,
  foothold7,
  foothold8,
  foothold9,
  foothold10,
  jug1,
  jug2,
  pinch1,
  pinch2,
  pinch3,
  pinch4,
  pinch5,
  pinch6,
  pinch7,
  pinch8
]

rock_wall = RockWall(boulders, 10)

class ClimbingState:
    def __init__(self, pairs, path=[]):
        self.pairs = pairs # List of holds currently being used by each limb
        self.path = path  # List of moves/actions taken to reach this state

class ClimbingAction:
    def __init__(self, move_type, hold_from, hold_to):
        self.move_type = move_type  # Type of move (e.g., regular move, flagging, heel hook, etc.)
        self.hold_from = hold_from  # Starting hold for the move
        self.hold_to = hold_to  # Ending hold for the move

class RockClimbingSolver:
    def __init__(self, rock_wall):
        self.rock_wall = rock_wall

    def is_goal_state(self, current_holds, finish_holds):
        pass
    
    def evaluate_state(self, current_state):
        # Simple evaluation function
        wall_angle_factor = self.evaluate_wall_angle(current_state)
        hold_quality_factor = self.evaluate_hold_quality(current_state)
        stretch_factor = self.evaluate_stretch(current_state)

        # You can adjust weights for each factor based on their importance
        value = 0.5 * wall_angle_factor + 0.3 * hold_quality_factor + 0.2 * stretch_factor
        return value

    def evaluate_wall_angle(self, current_state):
        # Example: Penalize for overhangs, reward for slabs
        return -abs(self.rock_wall.angle) / 180.0

    def evaluate_hold_quality(self, current_state):
        # Example: Assume the better the hold, the higher the score
        hold_quality = sum(hold.size for hold in current_state.current_holds if hold.size is not None)
        return hold_quality / len(current_state.current_holds) if current_state.current_holds else 0.0

    def evaluate_stretch(self, current_state):
        # Example: Penalize for excessive stretching
        max_stretch = max(hold.x_coord for hold in current_state.current_holds) - min(hold.x_coord for hold in current_state.current_holds)
        return 1.0 - (max_stretch / self.rock_wall.angle)

    def generate_successors(self, current_state):
        successors = []

        for hold_from in current_state.current_holds:
            for hold_to in self.rock_wall.boulders:
                if hold_to not in current_state.current_holds:
                    successors.append(ClimbingState(current_state.current_holds + [hold_to],
                                                     current_state.path + [ClimbingAction("Move", hold_from, hold_to)]))

        return successors

    def solve(self, start_holds, finish_holds):
        start_state = ClimbingState(start_holds)
        stack = [start_state]
        visited_states = set()

        while stack:
            current_state = stack.pop()
            print('running')

            if self.is_goal_state(current_state.current_holds, finish_holds):
                return current_state.path

            # Add the current state to the visited set
            visited_states.add(tuple(current_state.current_holds))

            successors = self.generate_successors(current_state)
            # Only consider successors that haven't been visited yet
            unvisited_successors = [succ for succ in successors if tuple(succ.current_holds) not in visited_states]
            stack.extend(unvisited_successors)

        return None

# Example usage:
solver = RockClimbingSolver(rock_wall)
start_holds = [foothold1, jug1]
finish_holds = [jug2]

optimal_path = solver.solve(start_holds, finish_holds)
print(optimal_path)


