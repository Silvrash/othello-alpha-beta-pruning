from OthelloEvaluator import OthelloEvaluator
from OthelloAlgorithm import OthelloAlgorithm
from OthelloAction import OthelloAction
from OthelloPosition import OthelloPosition
import time
import sys
from Node import Node


class StopSignal(Exception):
    """
    Exception raised when the time limit is exceeded during search.

    This exception is used to gracefully terminate the alpha-beta search
    when the allocated time limit is reached, allowing the algorithm to
    return the best move found so far.
    """

    pass


class AlphaBeta(OthelloAlgorithm):
    """
    This is where you implement the alpha-beta algorithm.
        See OthelloAlgorithm for details

    Author:
    """

    DefaultDepth = 5

    def __init__(self, othello_evaluator: OthelloEvaluator, depth=DefaultDepth):
        self.evaluator = othello_evaluator
        self.search_depth = depth
        self.evaluator = othello_evaluator
        self.search_depth = depth
        self.time_limit = None
        self.start_time = None
        self.nodes_searched = 0

        # to be safe, we increase the recursion limit for deep searches
        sys.setrecursionlimit(5000)

    def set_evaluator(self, othello_evaluator):
        """
        Set the heuristic evaluator for position evaluation.

        Args:
            othello_evaluator (OthelloEvaluator): The evaluator to use
        """
        self.evaluator = othello_evaluator

    def set_search_depth(self, depth):
        """
        Set the maximum search depth for the algorithm.

        Args:
            depth (int): Maximum depth to search
        """
        self.search_depth = depth

    def set_time_limit(self, time_limit, start_time=None):
        """
        Set the time limit for the search.

        Args:
            time_limit (float): Maximum time allowed for search in seconds
            start_time (float): Optional start time, if None uses current time
        """
        self.start_time = start_time if start_time is not None else time.time()
        self.time_limit = time_limit
        self.nodes_searched = 0  # Reset node counter

    def __force_stop_if_time_elapsed(self):
        """
        Check if time limit has been exceeded and raise StopSignal if so.

        This method is called during search to ensure the algorithm
        respects the time limit and can gracefully terminate.

        Raises:
            StopSignal: When time limit is exceeded
        """

        if self.start_time and self.time_limit and (time.time() - self.start_time) >= self.time_limit:
            raise StopSignal()

    def evaluate(self, othello_position: OthelloPosition) -> OthelloAction:
        """
        Evaluate the given position and return the best move.

        This method initiates the alpha-beta search from the given position.
        It starts the minimax search with alpha=-inf and beta=+inf.

        Args:
            othello_position (OthelloPosition): The position to evaluate

        Returns:
            OthelloAction: The best move found by the algorithm
        """

        best_action = self.max_value(othello_position, float("-inf"), float("inf"), self.search_depth)
        return best_action

    def max_value(self, pos: OthelloPosition, alpha: float, beta: float, depth: int):
        """
        Maximize the score for the current player (MAX node).

        This method implements the MAX part of the minimax algorithm.
        It tries to find the move that maximizes the score for the
        current player while respecting alpha-beta pruning.

        Args:
            pos (OthelloPosition): Current game position
            alpha (float): Alpha bound for pruning
            beta (float): Beta bound for pruning
            depth (int): Current search depth

        Returns:
            OthelloAction: Best move for the current player
        """

        # Check time limit before proceeding
        if self.nodes_searched % 1000 == 0:
            self.__force_stop_if_time_elapsed()

        self.nodes_searched += 1

        possible_moves = pos.get_moves()

        # Terminal condition: reached maximum depth
        if depth == 0:
            value = self.evaluator.evaluate(pos)
            # Dummy action to carry evaluation value
            leaf = OthelloAction(0, 0, False)
            leaf.value = value
            return leaf

        # Initialize best value and action
        best_value = float("-inf")
        best_action = None

        # Handle case with no legal moves
        if not possible_moves:
            possible_moves = [OthelloAction(0, 0, True)]

        # Sort moves by priority to improve alpha-beta pruning efficiency
        # Higher priority moves are searched first
        possible_moves.sort(key=self.evaluator.move_priority, reverse=True)

        for action in possible_moves:
            # Time control check
            self.__force_stop_if_time_elapsed()

            # Make move and evaluate resulting position
            child_pos = pos.make_move(action)
            min_action = self.min_value(child_pos, alpha, beta, depth - 1)

            # Update best move if this is better
            if min_action.value > best_value:
                best_value = min_action.value
                best_action = action

            # Update alpha bound
            alpha = max(alpha, best_value)

            # Alpha-beta pruning: stop if alpha >= beta
            if alpha >= beta:
                break  # Beta cutoff

        best_action.value = best_value
        return best_action

    def min_value(self, pos: OthelloPosition, alpha: float, beta: float, depth: int):
        """
        Minimize the score for the opponent (MIN node).

        This method implements the MIN part of the minimax algorithm.
        It tries to find the move that minimizes the score for the
        current player (maximizes opponent's advantage) while respecting
        alpha-beta pruning.

        Args:
            pos (OthelloPosition): Current game position
            alpha (float): Alpha bound for pruning
            beta (float): Beta bound for pruning
            depth (int): Current search depth

        Returns:
            OthelloAction: Best move for the opponent
        """
        # Check time limit before proceeding
        if self.nodes_searched % 1000 == 0:
            self.__force_stop_if_time_elapsed()

        self.nodes_searched += 1

        # Get possible moves for opponent
        possible_moves = pos.get_moves()

        # Terminal condition: reached maximum depth
        if depth == 0:
            value = self.evaluator.evaluate(pos)
            # Dummy action to carry evaluation value
            leaf = OthelloAction(0, 0, False)
            leaf.value = value
            return leaf

        # Initialize best value and action for MIN player
        best_value = float("inf")
        best_action = None

        # Handle case with no legal moves
        if not possible_moves:
            possible_moves = [OthelloAction(0, 0, True)]

        # Sort moves by priority to improve alpha-beta pruning efficiency
        possible_moves.sort(key=self.evaluator.move_priority, reverse=True)

        for action in possible_moves:
            # Time control check
            self.__force_stop_if_time_elapsed()

            # Make move and evaluate resulting position
            child_pos = pos.make_move(action)
            max_action = self.max_value(child_pos, alpha, beta, depth - 1)

            # Update best move if this minimizes opponent's score
            if max_action.value < best_value:
                best_value = max_action.value
                best_action = action

            # Update beta bound
            beta = min(beta, best_value)

            # Alpha-beta pruning: stop if alpha >= beta
            if beta <= alpha:
                break  # Alpha cutoff

        best_action.value = best_value
        return best_action
