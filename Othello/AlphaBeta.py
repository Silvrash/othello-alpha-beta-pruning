import time
from PrimaryEvaluator import PrimaryEvaluator
from OthelloPosition import OthelloPosition
from OthelloAlgorithm import OthelloAlgorithm
from OthelloAction import OthelloAction
import sys


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
    Alpha-Beta pruning algorithm implementation for Othello.
    
    This class implements the minimax algorithm with alpha-beta pruning
    for optimal move selection in Othello. It uses iterative deepening
    and sophisticated move ordering to maximize search efficiency.
    
    The algorithm maintains alpha and beta bounds to prune branches
    that cannot improve the current best move, significantly reducing
    the search space.
    
    Attributes:
        evaluator (OthelloEvaluator): Heuristic evaluation function
        search_depth (int): Maximum search depth
        time_limit (float): Time limit for search
        start_time (float): Search start time
        look_up_table (dict): Transposition table for caching
    
    Author: Afrasah Benjamin Arko & Sienichev Matvey
    """

    DefaultDepth = 5  # Default search depth

    def __init__(self, othello_evaluator=PrimaryEvaluator, depth=DefaultDepth):
        """
        Initialize the Alpha-Beta algorithm.
        
        Args:
            othello_evaluator (OthelloEvaluator): Heuristic evaluation function
            depth (int): Default search depth
        """
        self.evaluator = othello_evaluator
        self.search_depth = depth
        self.time_limit = None
        self.start_time = None
        sys.setrecursionlimit(5000)  # Increase recursion limit for deep searches

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

    def set_time_limit(self, time_limit):
        """
        Set the time limit for the search.
        
        Args:
            time_limit (float): Maximum time allowed for search in seconds
        """
        self.start_time = time.time()
        self.time_limit = time_limit

    def __force_stop_if_time_elapsed(self):
        """
        Check if time limit has been exceeded and raise StopSignal if so.
        
        This method is called during search to ensure the algorithm
        respects the time limit and can gracefully terminate.
        
        Raises:
            StopSignal: When time limit is exceeded
        """
        if (
            self.start_time
            and self.time_limit
            and (time.time() - self.start_time) >= self.time_limit
        ):
            raise StopSignal()

    def evaluate(self, othello_position: OthelloPosition) -> OthelloAction:
        """
        Evaluate the given position and return the best move.
        
        This method initiates the alpha-beta search from the given position.
        It starts the minimax search with alpha=-∞ and beta=+∞.
        
        Args:
            othello_position (OthelloPosition): The position to evaluate
            
        Returns:
            OthelloAction: The best move found by the algorithm
        """
        return self.max_value(othello_position, float("-inf"), float("inf"), 0)

    def max_value(
        self, pos: OthelloPosition, alpha: float, beta: float, depth: int
    ) -> OthelloAction:
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
        self.__force_stop_if_time_elapsed()
        possible_moves = pos.get_moves()

        # Terminal condition: reached maximum depth
        if depth == self.search_depth:
            val = self.evaluator.evaluate(pos)
            # Create dummy action to carry evaluation value
            leaf = OthelloAction(0, 0, False)
            leaf.value = val
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
            best_child_move = self.min_value(child_pos, alpha, beta, depth + 1)
            child_value = best_child_move.value

            # Update best move if this is better
            if child_value > best_value:
                best_value = child_value
                best_action = action
                best_action.value = child_value

            # Update alpha bound
            alpha = max(alpha, best_value)

            # Alpha-beta pruning: stop if alpha >= beta
            if alpha >= beta:
                break  # Beta cutoff

        return best_action

    def min_value(
        self, pos: OthelloPosition, alpha: float, beta: float, depth: int
    ) -> OthelloAction:
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
        self.__force_stop_if_time_elapsed()

        # Get possible moves for opponent
        possible_moves = pos.get_moves()

        # Terminal condition: reached maximum depth
        if depth == self.search_depth:
            val = self.evaluator.evaluate(pos)
            # Create dummy action to carry evaluation value
            leaf = OthelloAction(0, 0, False)
            leaf.value = val
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
            best_child_move = self.max_value(child_pos, alpha, beta, depth + 1)
            child_value = best_child_move.value

            # Update best move if this minimizes opponent's score
            if child_value < best_value:
                best_value = child_value
                best_action = action
                best_action.value = child_value

            # Update beta bound
            beta = min(beta, best_value)
            
            # Alpha-beta pruning: stop if alpha >= beta
            if beta <= alpha:
                break  # Alpha cutoff

        return best_action

    