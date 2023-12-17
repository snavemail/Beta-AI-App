from classes.PriorityQueue import PriorityQueue
from copy import copy
from utils import state_difficulty, move_difficulty, move_to_text


class RouteFinder:
    """
    Class to find the route of a wall
    Takes in a state and gets the person's reach from that
    """

    WALL_HEIGHT = 180

    def __init__(self, state):
        self.state = state
        self.reach = state.person.reach

    def get_cost_value(self, costs):
        """
        Helper function used to square the costs in the list of costs
        """
        return sum([cost for cost in costs]) + 250 * len(costs)

    def uniform_cost_search(self):
        """
        Search function to find the best route
        """
        explored = []
        frontier = PriorityQueue()
        num = 0
        frontier.push(self.state, 0)
        while not frontier.isEmpty():
            cur_state = frontier.pop()
            explored.append(cur_state)
            if (
                cur_state.lh.hold == self.state.route.finish_hold
                and cur_state.rh.hold == self.state.route.finish_hold
            ):
                # What every good rock climber says at the top
                print("TAAAAAAAAAAAAAAKE")
                print(cur_state.costs)
                print(self.get_cost_value(cur_state.costs))
                return cur_state.moves
            for next_state, action in cur_state.getStateSuccessors():
                if next_state not in explored:
                    num += 1
                    if num % 500 == 0:
                        print(
                            f"Checking state #{num} with move length {len(cur_state.moves)}"
                        )
                    next_state.costs = copy(cur_state.costs)
                    next_state.costs.append(
                        state_difficulty(next_state)
                        + move_difficulty(cur_state, action[0], action[1])
                    )
                    next_state.moves = copy(cur_state.moves)
                    next_state.moves.append(action)
                    if next_state in [tup[2] for tup in frontier.heap]:
                        frontier.update(
                            next_state, self.get_cost_value(next_state.costs)
                        )
                    else:
                        frontier.push(next_state, self.get_cost_value(next_state.costs))
        return []

    def get_moves(self):
        """
        Returns the moves of the best route
        """
        results = self.uniform_cost_search()
        for action in results:
            print(move_to_text(action, self.route))
        return results
