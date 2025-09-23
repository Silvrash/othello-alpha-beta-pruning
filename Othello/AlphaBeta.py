import time
from PrimaryEvaluator import PrimaryEvaluator
from OthelloAlgorithm import OthelloAlgorithm
from OthelloAction import OthelloAction
import sys
from BitboardOthelloPosition import BitboardOthelloPosition

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
        self.transposition_table = {}  # Transposition table for caching
        self.nodes_searched = 0  # Counter for debugging
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
        # Don't clear transposition table - we want to reuse previous evaluations
        self.nodes_searched = 0  # Reset node counter

    def _get_position_key(self, pos: BitboardOthelloPosition) -> int:
        """
        Generate a unique key for a position (without depth) for transposition table.
        This allows us to reuse evaluations from shallower depths.
        
        Args:
            pos (BitboardOthelloPosition): The position
            
        Returns:
            int: Unique key for the position
        """
        return hash((pos.white_bitboard, pos.black_bitboard, pos.maxPlayer))

    def _lookup_transposition(self, pos: BitboardOthelloPosition, depth: int, alpha: float, beta: float):
        """
        Look up a position in the transposition table.
        Can use evaluations from any depth >= current depth.
        
        Args:
            pos (BitboardOthelloPosition): The position
            depth (int): The search depth
            alpha (float): Alpha bound
            beta (float): Beta bound
            
        Returns:
            tuple: (found, value, move) or (False, None, None)
        """
        key = self._get_position_key(pos)
        if key in self.transposition_table:
            entry = self.transposition_table[key]
            value, move, entry_type, entry_depth = entry
            
            # Use this entry if it's from a search depth >= current depth
            if entry_depth >= depth:
                if entry_type == "exact":
                    return True, value, move
                elif entry_type == "lower" and value >= beta:
                    return True, value, move
                elif entry_type == "upper" and value <= alpha:
                    return True, value, move
        
        return False, None, None

    def _store_transposition(self, pos: BitboardOthelloPosition, depth: int, value: float, move, alpha: float, beta: float):
        """
        Store a position in the transposition table.
        
        Args:
            pos (BitboardOthelloPosition): The position
            depth (int): The search depth
            value (float): The evaluation value
            move: The best move
            alpha (float): Alpha bound
            beta (float): Beta bound
        """
        key = self._get_position_key(pos)
        
        if value <= alpha:
            entry_type = "upper"
        elif value >= beta:
            entry_type = "lower"
        else:
            entry_type = "exact"
            
        self.transposition_table[key] = (value, move, entry_type, depth)

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
        

    def evaluate(self, othello_position: BitboardOthelloPosition) -> OthelloAction:
        """
        Evaluate the given position and return the best move.
        
        This method initiates the alpha-beta search from the given position.
        It starts the minimax search with alpha=-∞ and beta=+∞.
        
        Args:
            othello_position (OthelloPosition): The position to evaluate
            
        Returns:
            OthelloAction: The best move found by the algorithm
        """

        # root = Node(othello_position, self.search_depth, evaluator=self.evaluator, time_control=self.__force_stop_if_time_elapsed)
        # return root.best_move

        return self.max_value(othello_position, float("-inf"), float("inf"), 0)

    def max_value(
        self, pos: BitboardOthelloPosition, alpha: float, beta: float, depth: int
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
        # Check time limit before proceeding (less frequent for better performance)
        if self.nodes_searched % 1000 == 0:  # Check every 1000 nodes
            self.__force_stop_if_time_elapsed()
        self.nodes_searched += 1

        # Check transposition table
        # found, value, move = self._lookup_transposition(pos, depth, alpha, beta)
        # if found:
        #     return move

        possible_moves = pos.get_moves()

        # Terminal condition: reached maximum depth
        if depth == self.search_depth:
            val = self.evaluator.evaluate(pos, None)  # No action for leaf nodes
            # Create dummy action to carry evaluation value
            leaf = OthelloAction(0, 0, False)
            leaf.value = val
            self._store_transposition(pos, depth, val, leaf, alpha, beta)
            return leaf

        # Initialize best value and action
        best_value = float("-inf")
        best_action = None
        original_alpha = alpha

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
            child_pos, flip_count = pos.make_move(action)
            best_child_move = self.min_value(child_pos, alpha, beta, depth + 1)
            child_value = best_child_move.value

            # Update best move if this is better
            if child_value > best_value:
                best_value = child_value
                best_action = action
                best_action.value = child_value
                best_action.discs_flipped = flip_count

            # Update alpha bound
            alpha = max(alpha, best_value)

            # Alpha-beta pruning: stop if alpha >= beta
            if alpha >= beta:
                break  # Beta cutoff

        # Store in transposition table
        self._store_transposition(pos, depth, best_value, best_action, original_alpha, beta)

        return best_action

    def min_value(
        self, pos: BitboardOthelloPosition, alpha: float, beta: float, depth: int
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
        # Check time limit before proceeding (less frequent for better performance)
        if self.nodes_searched % 1000 == 0:  # Check every 1000 nodes
            self.__force_stop_if_time_elapsed()
        self.nodes_searched += 1

        # Check transposition table
        # found, value, move = self._lookup_transposition(pos, depth, alpha, beta)
        # if found:
        #     return move

        # Get possible moves for opponent
        possible_moves = pos.get_moves()

        # Terminal condition: reached maximum depth
        if depth == self.search_depth:
            val = self.evaluator.evaluate(pos, None)  # No action for leaf nodes
            # Create dummy action to carry evaluation value
            leaf = OthelloAction(0, 0, False)
            leaf.value = val
            self._store_transposition(pos, depth, val, leaf, alpha, beta)
            return leaf

        # Initialize best value and action for MIN player
        best_value = float("inf")
        best_action = None
        original_beta = beta

        # Handle case with no legal moves
        if not possible_moves:
            possible_moves = [OthelloAction(0, 0, True)]
        
        # Sort moves by priority to improve alpha-beta pruning efficiency
        possible_moves.sort(key=self.evaluator.move_priority, reverse=True)

        for action in possible_moves:
            # Time control check
            self.__force_stop_if_time_elapsed()

            # Make move and evaluate resulting position
            child_pos, flip_count = pos.make_move(action)
            best_child_move = self.max_value(child_pos, alpha, beta, depth + 1)
            child_value = best_child_move.value

            # Update best move if this minimizes opponent's score
            if child_value < best_value:
                best_value = child_value
                best_action = action
                best_action.value = child_value
                best_action.discs_flipped = flip_count
            # Update beta bound
            beta = min(beta, best_value)
            
            # Alpha-beta pruning: stop if alpha >= beta
            if beta <= alpha:
                break  # Alpha cutoff

        # Store in transposition table
        self._store_transposition(pos, depth, best_value, best_action, alpha, original_beta)

        return best_action

    