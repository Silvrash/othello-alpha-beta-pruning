from OthelloEvaluator import OthelloEvaluator
from BitboardOthelloPosition import BitboardOthelloPosition

"""
  A simple evaluator that just counts the number of black and white squares 
  Author: Ola Ringdahl
  Updated for BitboardOthelloPosition by AI Assistant
"""


class CountingEvaluator(OthelloEvaluator):
    def evaluate(self, othello_position: BitboardOthelloPosition, action = None):
        # Count pieces using bitboard operations
        white_squares = bin(othello_position.white_bitboard).count('1')
        black_squares = bin(othello_position.black_bitboard).count('1')

        if othello_position.maxPlayer:
            return white_squares - black_squares
        else:
            return black_squares - white_squares
