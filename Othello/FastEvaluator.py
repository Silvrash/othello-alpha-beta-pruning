from OthelloAction import OthelloAction
from OthelloEvaluator import OthelloEvaluator
from BitboardOthelloPosition import BitboardOthelloPosition

class FastEvaluator(OthelloEvaluator):
    """
    Fast, lightweight evaluator designed specifically to beat naive counting AI.
    
    Strategy: Since the naive AI uses only piece counting at fixed depth 7,
    we need to achieve deeper search and make better strategic decisions.
    """
    
    def __init__(self):
        # Pre-computed corner mask for fast corner detection
        self.corner_mask = (1 << 0) | (1 << 7) | (1 << 56) | (1 << 63)
        
        # X-squares (dangerous diagonal positions next to corners)
        self.x_square_mask = (1 << 9) | (1 << 14) | (1 << 49) | (1 << 54)
        
        # Edge positions (stable but not corners)
        self.edge_mask = (
            # Top edge: bits 1-6
            (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6) |
            # Bottom edge: bits 57-62
            (1 << 57) | (1 << 58) | (1 << 59) | (1 << 60) | (1 << 61) | (1 << 62) |
            # Left edge: bits 8,16,24,32,40,48
            (1 << 8) | (1 << 16) | (1 << 24) | (1 << 32) | (1 << 40) | (1 << 48) |
            # Right edge: bits 15,23,31,39,47,55
            (1 << 15) | (1 << 23) | (1 << 31) | (1 << 39) | (1 << 47) | (1 << 55)
        )
    
    def evaluate(self, othello_position: BitboardOthelloPosition, action) -> float:
        """
        Fast evaluation designed specifically to beat naive counting AI.
        
        Key insight: Naive AI only counts pieces, so we need to:
        1. Get more pieces by endgame (match their strategy)
        2. Use superior tactics (corners, mobility) to achieve this
        3. Search deeper due to faster evaluation
        """
        
        # Get bitboards for current player and opponent
        if not othello_position.maxPlayer:
            my_bitboard = othello_position.white_bitboard
            opp_bitboard = othello_position.black_bitboard
        else:
            my_bitboard = othello_position.black_bitboard
            opp_bitboard = othello_position.white_bitboard
        
        # Count pieces
        my_pieces = bin(my_bitboard).count('1')
        opp_pieces = bin(opp_bitboard).count('1')
        total_pieces = my_pieces + opp_pieces
        
        score = 0
        
        # 1. Piece count (what the naive AI uses) - always important
        piece_diff = my_pieces - opp_pieces
        score += piece_diff * 1
        
        # 2. Corner control - extremely valuable
        my_corners = bin(my_bitboard & self.corner_mask).count('1')
        opp_corners = bin(opp_bitboard & self.corner_mask).count('1')
        corner_diff = my_corners - opp_corners
        score += corner_diff * 25
        
        # 3. Avoid X-squares early in game
        if total_pieces < 40:
            my_x_squares = bin(my_bitboard & self.x_square_mask).count('1')
            opp_x_squares = bin(opp_bitboard & self.x_square_mask).count('1')
            x_square_penalty = my_x_squares - opp_x_squares
            score -= x_square_penalty * 10
        
        # 4. Mobility - having more moves is good
        if total_pieces < 50:  # Don't compute in very late game for speed
            my_mobility = len(othello_position.get_moves())
            # Quick mobility estimate for opponent without full position clone
            # This is an approximation but much faster
            score += my_mobility * 0.5
        
        # 5. Edge control (stable pieces)
        my_edges = bin(my_bitboard & self.edge_mask).count('1')
        opp_edges = bin(opp_bitboard & self.edge_mask).count('1')
        edge_diff = my_edges - opp_edges
        score += edge_diff * 2
        
        return score

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
        base_value = 1

        # Add mobility bonus (moves that give more options are better)
        # This is a heuristic - moves that create more future moves are prioritized
        mobility_bonus = 0

        # Corner moves get highest priority
        if (row_idx, col_idx) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            mobility_bonus = 2000

        # X-squares get lowest priority (most dangerous)
        elif (row_idx, col_idx) in [(1, 1), (1, 6), (6, 1), (6, 6)]:
            mobility_bonus = -2000

        # C-squares get low priority (dangerous)
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
            mobility_bonus = -1000

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
            mobility_bonus = 200

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
            mobility_bonus = 20

        return base_value + mobility_bonus
