from OthelloEvaluator import OthelloEvaluator
from BitboardOthelloPosition import BitboardOthelloPosition

class BeatNaiveEvaluator(OthelloEvaluator):
    """
    Evaluator designed specifically to beat a naive counting AI at depth 7.
    
    Strategy: Use mostly piece counting like the naive AI, but add just enough
    tactical knowledge to make better decisions at the same search depth.
    """
    
    def __init__(self):
        # Corner positions - most stable
        self.corner_mask = (1 << 0) | (1 << 7) | (1 << 56) | (1 << 63)
        
        # X-squares - dangerous positions next to corners
        self.x_square_mask = (1 << 9) | (1 << 14) | (1 << 49) | (1 << 54)
    
    def evaluate(self, othello_position: BitboardOthelloPosition, action) -> float:
        """
        Simple evaluation that's mostly piece counting with minimal tactical additions.
        
        This should be almost as fast as CountingEvaluator but slightly smarter.
        """
        
        # Get piece counts using fast bitboard operations
        white_pieces = bin(othello_position.white_bitboard).count('1')
        black_pieces = bin(othello_position.black_bitboard).count('1')
        
        if othello_position.maxPlayer:
            my_pieces = white_pieces
            opp_pieces = black_pieces
            my_bitboard = othello_position.white_bitboard
            opp_bitboard = othello_position.black_bitboard
        else:
            my_pieces = black_pieces
            opp_pieces = white_pieces
            my_bitboard = othello_position.black_bitboard
            opp_bitboard = othello_position.white_bitboard
        
        # Base score: piece difference (like naive AI)
        piece_diff = my_pieces - opp_pieces
        
        # Add small bonuses for strategic positions
        my_corners = bin(my_bitboard & self.corner_mask).count('1')
        opp_corners = bin(opp_bitboard & self.corner_mask).count('1')
        corner_bonus = (my_corners - opp_corners) * 5  # Small but significant
        
        # Small penalty for X-squares (only in early/mid game)
        total_pieces = my_pieces + opp_pieces
        x_square_penalty = 0
        if total_pieces < 45:  # Only in early/mid game
            my_x_squares = bin(my_bitboard & self.x_square_mask).count('1')
            opp_x_squares = bin(opp_bitboard & self.x_square_mask).count('1')
            x_square_penalty = (my_x_squares - opp_x_squares) * 2
        
        return piece_diff + corner_bonus - x_square_penalty
    
    def move_priority(self, action):
        """
        Very simple move ordering.
        """
        if action.is_pass_move:
            return float("-inf")
        
        bit_pos = (action.row - 1) * 8 + (action.col - 1)
        
        # Corners are highest priority
        if self.corner_mask & (1 << bit_pos):
            return 100
        
        # X-squares are lowest priority  
        elif self.x_square_mask & (1 << bit_pos):
            return -100
        
        # Everything else is equal
        else:
            return 0
