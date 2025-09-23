from OthelloAction import OthelloAction
from OthelloEvaluator import OthelloEvaluator
from BitboardOthelloPosition import BitboardOthelloPosition

class GreedyEvaluator(OthelloEvaluator):
    """
    Simplified evaluator implementing the three classic Othello principles:
    1. Mobility - Maximize our moves, minimize opponent's moves
    2. Stability - Aim for stable (un-flippable) discs, especially corners
    3. Parity - Favor being the last to move
    
    Uses a greedy approach in the late game focused on piece count.
    """
    
    def __init__(self):
        # Corner positions - most stable
        self.corner_mask = (1 << 0) | (1 << 7) | (1 << 56) | (1 << 63)
        
        # X-squares - dangerous positions next to corners
        self.x_square_mask = (1 << 9) | (1 << 14) | (1 << 49) | (1 << 54)
        
        # Edge positions (stable but not corners)
        self.edge_mask = (
            # Top and bottom edges (excluding corners)
            (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6) |
            (1 << 57) | (1 << 58) | (1 << 59) | (1 << 60) | (1 << 61) | (1 << 62) |
            # Left and right edges (excluding corners)
            (1 << 8) | (1 << 16) | (1 << 24) | (1 << 32) | (1 << 40) | (1 << 48) |
            (1 << 15) | (1 << 23) | (1 << 31) | (1 << 39) | (1 << 47) | (1 << 55)
        )
    
    def evaluate(self, othello_position: BitboardOthelloPosition, action) -> float:
        """
        Evaluate position using the three classic Othello principles with greedy endgame.
        """
        # Get bitboards for current player and opponent
        if othello_position.maxPlayer:
            my_bitboard = othello_position.white_bitboard
            opp_bitboard = othello_position.black_bitboard
        else:
            my_bitboard = othello_position.black_bitboard
            opp_bitboard = othello_position.white_bitboard
        
        # Count pieces
        my_pieces = bin(my_bitboard).count('1')
        opp_pieces = bin(opp_bitboard).count('1')
        total_pieces = my_pieces + opp_pieces
        
        # 1. MOBILITY - "Maximize moves, minimize opponent moves"
        my_mobility = len(othello_position.get_moves())
        temp_pos = othello_position.clone()
        temp_pos.maxPlayer = not othello_position.maxPlayer
        opp_mobility = len(temp_pos.get_moves())
        mobility_diff = my_mobility - opp_mobility
        
        # 2. CORNER CONTROL - Most stable positions
        my_corners = bin(my_bitboard & self.corner_mask).count('1')
        opp_corners = bin(opp_bitboard & self.corner_mask).count('1')
        corner_diff = my_corners - opp_corners
        
        # 3. PARITY - Favor being last to move
        parity_bonus = self._calculate_parity(total_pieces, my_pieces, opp_pieces)
        
        # 4. PIECE COUNT
        piece_diff = my_pieces - opp_pieces
        
        # DYNAMIC PHASE EVALUATION
        if total_pieces < 20:
            # EARLY GAME: Focus on mobility and avoid X-squares
            return self._early_game_eval(mobility_diff, corner_diff, parity_bonus, 
                                       piece_diff, my_bitboard, opp_bitboard)
        elif total_pieces < 45:
            # MID GAME: Balance all factors
            return self._mid_game_eval(mobility_diff, corner_diff, parity_bonus,
                                     piece_diff, my_bitboard, opp_bitboard)
        else:
            # LATE GAME: GREEDY APPROACH - Focus on piece count
            return self._late_game_greedy(mobility_diff, corner_diff, parity_bonus, piece_diff)
    
    def _early_game_eval(self, mobility_diff, corner_diff, parity_bonus, piece_diff, my_bitboard, opp_bitboard):
        """Early game: Maximize mobility, avoid X-squares"""
        score = 0
        
        # Mobility is king in early game
        score += mobility_diff * 100
        
        # Corner control
        score += corner_diff * 1000
        
        # Avoid X-squares
        my_x_squares = bin(my_bitboard & self.x_square_mask).count('1')
        opp_x_squares = bin(opp_bitboard & self.x_square_mask).count('1')
        score -= (my_x_squares - opp_x_squares) * 500
        
        # Small parity consideration
        score += parity_bonus * 10
        
        # Piece count is secondary
        score += piece_diff * 5
        
        return score
    
    def _mid_game_eval(self, mobility_diff, corner_diff, parity_bonus, piece_diff, my_bitboard, opp_bitboard):
        """Mid game: Balance mobility, corners, and positioning"""
        score = 0
        
        # Corner control becomes very important
        score += corner_diff * 2000
        
        # Mobility still matters
        score += mobility_diff * 80
        
        # Edge control for stability
        my_edges = bin(my_bitboard & self.edge_mask).count('1')
        opp_edges = bin(opp_bitboard & self.edge_mask).count('1')
        score += (my_edges - opp_edges) * 50
        
        # Parity becomes more important
        score += parity_bonus * 30
        
        # Piece count grows in importance
        score += piece_diff * 20
        
        return score
    
    def _late_game_greedy(self, mobility_diff, corner_diff, parity_bonus, piece_diff):
        """Late game: GREEDY APPROACH - Maximize piece count"""
        score = 0
        
        # GREEDY: Piece count dominates everything
        score += piece_diff * 300  # Massive weight for pieces
        
        # Parity is critical for getting final pieces
        score += parity_bonus * 100
        
        # Mobility for accessing remaining squares
        score += mobility_diff * 60
        
        # Corners still matter for stability
        score += corner_diff * 800
        
        # Greedy bonus for being significantly ahead
        if piece_diff > 3:
            score += piece_diff * 100  # Compound advantage
        
        return score
    
    def _calculate_parity(self, total_pieces, my_pieces, opp_pieces):
        """Calculate parity advantage for being last to move"""
        remaining_squares = 64 - total_pieces
        piece_diff = my_pieces - opp_pieces
        
        parity_score = 0
        
        # Overall game parity
        if remaining_squares % 2 == 0:
            if piece_diff >= 0:
                parity_score += 5
        else:
            if piece_diff <= 0:
                parity_score += 5
        
        # Tempo considerations
        if total_pieces < 40 and -2 <= piece_diff <= 0:
            parity_score += 5  # Being slightly behind can be good
        elif total_pieces >= 50 and piece_diff > 0:
            parity_score += piece_diff * 2  # Being ahead in endgame
        
        return parity_score
    
    def move_priority(self, action: OthelloAction) -> float:
        """Simple move ordering for alpha-beta pruning"""
        if action.is_pass_move:
            return float("-inf")
        
        # Convert to bit position
        bit_pos = (action.row - 1) * 8 + (action.col - 1)
        
        # Corner moves get highest priority
        if self.corner_mask & (1 << bit_pos):
            return 10000
        
        # X-square moves get lowest priority
        elif self.x_square_mask & (1 << bit_pos):
            return -10000
        
        # Edge moves get high priority
        elif self.edge_mask & (1 << bit_pos):
            return 1000
        
        # Everything else is neutral
        else:
            return 0
