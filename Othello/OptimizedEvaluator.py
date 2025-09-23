from OthelloEvaluator import OthelloEvaluator
from BitboardOthelloPosition import BitboardOthelloPosition
from OthelloAction import OthelloAction

class OptimizedEvaluator(OthelloEvaluator):
    """
    Optimized evaluator that combines simple piece counting with sophisticated move ordering.
    
    This evaluator uses the same evaluation function as the naive AI (piece counting)
    but with much better move ordering to improve alpha-beta pruning efficiency.
    
    Author: AI Assistant
    """
    
    def __init__(self):
        # Pre-compute position values for move ordering
        self.position_values = self._compute_position_values()
    
    def _compute_position_values(self):
        """Compute position values for move ordering optimization."""
        values = {}
        
        # Corner positions (highest value)
        corners = [(0,0), (0,7), (7,0), (7,7)]
        for pos in corners:
            values[pos] = 1000
            
        # X-squares (most dangerous)
        x_squares = [(1,1), (1,6), (6,1), (6,6)]
        for pos in x_squares:
            values[pos] = -1000
            
        # C-squares (dangerous)
        c_squares = [(0,1), (1,0), (0,6), (1,7), (6,0), (7,1), (7,6), (6,7)]
        for pos in c_squares:
            values[pos] = -500
            
        # Edge positions (stable)
        edges = [(0,2), (0,3), (0,4), (0,5), (2,0), (3,0), (4,0), (5,0),
                (7,2), (7,3), (7,4), (7,5), (2,7), (3,7), (4,7), (5,7)]
        for pos in edges:
            values[pos] = 100
            
        # Center positions (good for early game)
        centers = [(2,2), (2,3), (2,4), (2,5), (3,2), (3,3), (3,4), (3,5),
                  (4,2), (4,3), (4,4), (4,5), (5,2), (5,3), (5,4), (5,5)]
        for pos in centers:
            values[pos] = 10
            
        return values
    
    def evaluate(self, othello_position: BitboardOthelloPosition) -> float:
        """
        Evaluate position using simple piece counting (same as naive AI).
        
        Args:
            othello_position (BitboardOthelloPosition): The position to evaluate
            
        Returns:
            float: Evaluation score (positive favors current player)
        """
        # Count pieces using bitboard operations
        white_squares = bin(othello_position.white_bitboard).count('1')
        black_squares = bin(othello_position.black_bitboard).count('1')

        if othello_position.maxPlayer:
            return white_squares - black_squares
        else:
            return black_squares - white_squares
    
    def move_priority(self, action: OthelloAction) -> float:
        """
        Calculate move priority for optimal alpha-beta pruning.
        
        This method uses sophisticated position analysis to order moves
        for maximum alpha-beta pruning efficiency.
        
        Args:
            action (OthelloAction): The move to evaluate
            
        Returns:
            float: Priority value for move ordering
        """
        # Pass moves get lowest priority
        if action.is_pass_move:
            return float("-inf")

        # Convert 1-indexed coordinates to 0-indexed
        row_idx = action.row - 1
        col_idx = action.col - 1
        
        # Get base position value
        base_value = self.position_values.get((row_idx, col_idx), 1)
        
        # Add mobility bonus (moves that give more options are better)
        # This is a heuristic - moves that create more future moves are prioritized
        mobility_bonus = 0
        
        # Corner moves get highest priority
        if (row_idx, col_idx) in [(0,0), (0,7), (7,0), (7,7)]:
            mobility_bonus = 2000
            
        # X-squares get lowest priority (most dangerous)
        elif (row_idx, col_idx) in [(1,1), (1,6), (6,1), (6,6)]:
            mobility_bonus = -2000
            
        # C-squares get low priority (dangerous)
        elif (row_idx, col_idx) in [(0,1), (1,0), (0,6), (1,7), (6,0), (7,1), (7,6), (6,7)]:
            mobility_bonus = -1000
            
        # Edge moves get medium priority
        elif (row_idx, col_idx) in [(0,2), (0,3), (0,4), (0,5), (2,0), (3,0), (4,0), (5,0),
                                   (7,2), (7,3), (7,4), (7,5), (2,7), (3,7), (4,7), (5,7)]:
            mobility_bonus = 200
            
        # Center moves get lower priority
        elif (row_idx, col_idx) in [(2,2), (2,3), (2,4), (2,5), (3,2), (3,3), (3,4), (3,5),
                                   (4,2), (4,3), (4,4), (4,5), (5,2), (5,3), (5,4), (5,5)]:
            mobility_bonus = 20
        
        return base_value + mobility_bonus
