from OthelloAction import OthelloAction
from OthelloPosition import EMPTY_PLACEHOLDER, OthelloPosition
from OthelloEvaluator import OthelloEvaluator
import numpy as np
from BitboardOthelloPosition import BitboardOthelloPosition


class SecondaryEvaluator(OthelloEvaluator):
    """
    Heuristic evaluator for Othello positions.

    This evaluator applies different strategies for different phases of the game such as early, middle, and late stages.
    It takes into account stability, positional control, and avoiding stability.

    Key features:
    - Corner control (highest priority)
    - Stable disc detection
    - X-square and C-square avoidance
    - Mobility calculation
    - Frontier square minimization
    - Edge and center control
    - Phase-adaptive weighting

    The evaluator uses bitboard operations for efficient calculation
    and pre-computed masks for different position types.

    Author: Afrasah Benjamin Arko & Sienichev Matvey
    """

    def evaluate(self, othello_position: BitboardOthelloPosition) -> float:
        # Get bitboards for current player and opponent
        if othello_position.maxPlayer:
            my_bitboard = othello_position.white_bitboard
            opp_bitboard = othello_position.black_bitboard
        else:
            my_bitboard = othello_position.black_bitboard
            opp_bitboard = othello_position.white_bitboard

        # --- Count discs using bitboard operations ---
        my_discs = bin(my_bitboard).count('1')
        opp_discs = bin(opp_bitboard).count('1')
        total_discs = my_discs + opp_discs

        # --- Game phase ---
        if total_discs <= 20:       # Early
            phase = "early"
        elif total_discs <= 58:     # Mid
            phase = "mid"
        else:                       # Late (endgame)
            phase = "late"

        # --- 1. Piece difference (disc count) ---
        piece_diff = 0
        if my_discs + opp_discs != 0:
            piece_diff = 100 * (my_discs - opp_discs) / (my_discs + opp_discs)

        # --- 2. Mobility ---
        my_moves = othello_position.get_moves()
        # Create a temporary position to get opponent moves
        temp_pos = othello_position.clone()
        temp_pos.maxPlayer = not temp_pos.maxPlayer
        opp_moves = temp_pos.get_moves()
        
        mobility = 0
        if len(my_moves) + len(opp_moves) != 0:
            mobility = 100 * (len(my_moves) - len(opp_moves)) / (len(my_moves) + len(opp_moves))

        # --- 3. Corners ---
        # Corner bit positions: (0,0)=0, (0,7)=7, (7,0)=56, (7,7)=63
        corner_bits = [0, 7, 56, 63]
        my_corners = sum(1 for bit in corner_bits if my_bitboard & (1 << bit))
        opp_corners = sum(1 for bit in corner_bits if opp_bitboard & (1 << bit))
        corner_score = 25 * (my_corners - opp_corners)

        # --- 4. Positional weights matrix ---
        weights = [
            [120, -20, 20, 5, 5, 20, -20, 120],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [20,  -5, 15, 3, 3, 15,  -5, 20],
            [5,   -5,  3, 3, 3,  3,  -5,  5],
            [5,   -5,  3, 3, 3,  3,  -5,  5],
            [20,  -5, 15, 3, 3, 15,  -5, 20],
            [-20, -40, -5, -5, -5, -5, -40, -20],
            [120, -20, 20, 5, 5, 20, -20, 120]
        ]
        
        positional = 0
        for r in range(8):
            for c in range(8):
                bit_pos = r * 8 + c
                if my_bitboard & (1 << bit_pos):
                    positional += weights[r][c]
                elif opp_bitboard & (1 << bit_pos):
                    positional -= weights[r][c]

        # --- Weighting by phase (scaled down to match counting evaluator range) ---
        if total_discs == 0:
            return 0  # Handle edge case of empty board
        
        if phase == "early":
            return ((0.5 * piece_diff) + (1 * mobility) + (5 * corner_score) + (1 * positional)) / 10

        elif phase == "mid":
            return ((0.5 * piece_diff) + (1 * mobility) + (8 * corner_score) + (0.5 * positional)) / 10

        else:  # late
            return ((1 * piece_diff) + (0.2 * mobility) + (100 * corner_score) + (1 * positional)) / 10
