from abc import ABC, abstractmethod
from OthelloAction import OthelloAction


class OthelloEvaluator(ABC):
    """
    This interface defines the mandatory methods for an evaluator, i.e., a class that can take a position and
    return an integer value that represents a heuristic evaluation of the position (positive numbers if the position is
    better for the first player, white). Notice that an evaluator is not supposed to make moves in the position to
    'see into the future', but only evaluate the static features of the postion.

    Author: Ola Ringdahl
    """

    @abstractmethod
    def evaluate(self, othello_position):
        """
        Evaluate an OthelloPosition
        :param othello_position: The OthelloPosition to evaluate
        :return: An integer representing a heuristic evaluation of the position
        """
        pass

    def move_priority(self, action: OthelloAction):
        """
        Calculate move priority for move ordering optimization.

        This method assigns priority values to moves to improve alpha-beta
        pruning efficiency. Higher priority moves are searched first,
        increasing the likelihood of early cutoffs.

        Priority order (highest to lowest):
        1. Corner moves (1000) - Most stable
        2. Edge moves (100) - Stable
        3. Center moves (10) - Good for early game
        4. Regular moves (1) - Neutral
        5. C-square moves (-500) - Dangerous
        6. X-square moves (-1000) - Most dangerous
        7. Pass moves (-∞) - Only when forced

        Args:
            action (OthelloAction): The move to evaluate

        Returns:
            float: Priority value for move ordering
        """
        # Pass moves get lowest priority
        if action.is_pass_move:
            return float("-inf")

        # Convert 1-indexed coordinates to 0-indexed for mask lookup
        row_idx = action.row - 1
        col_idx = action.col - 1

        # Corner moves get highest priority
        if (row_idx, col_idx) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            return 1000

        # X squares get lowest priority (most dangerous)
        elif (row_idx, col_idx) in [(1, 1), (1, 6), (6, 1), (6, 6)]:
            return -1000

        # C squares get low priority (dangerous)
        elif (row_idx, col_idx) in [
            (0, 1),
            (1, 0),
            (0, 6),
            (1, 7),
            (6, 0),
            (7, 1),
            (7, 6),
            (6, 7),
        ]:
            return -500

        # Edge moves get medium priority
        elif (row_idx, col_idx) in [
            (0, 2),
            (0, 3),
            (0, 4),
            (0, 5),
            (2, 0),
            (3, 0),
            (4, 0),
            (5, 0),
            (7, 2),
            (7, 3),
            (7, 4),
            (7, 5),
            (2, 7),
            (3, 7),
            (4, 7),
            (5, 7),
        ]:
            return 100

        # Center moves get lower priority
        elif (row_idx, col_idx) in [
            (2, 2),
            (2, 3),
            (2, 4),
            (2, 5),
            (3, 2),
            (3, 3),
            (3, 4),
            (3, 5),
            (4, 2),
            (4, 3),
            (4, 4),
            (4, 5),
            (5, 2),
            (5, 3),
            (5, 4),
            (5, 5),
        ]:
            return 10

        # Every other square gets neutral priority
        else:
            return 1
