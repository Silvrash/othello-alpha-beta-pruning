from OthelloEvaluator import OthelloEvaluator
import numpy as np

"""
  A simple evaluator that just counts the number of black and white squares 
  Author: Ola Ringdahl
"""


class CountingEvaluator(OthelloEvaluator):

    def __init__(self, playing_white):
        super().__init__()
        self.playing_white = playing_white

    def evaluate(self, othello_position):
        white_mask = othello_position.board == 'W'
        black_mask = othello_position.board == 'B'

        black_squares = np.sum(black_mask)
        white_squares = np.sum(white_mask)


        if othello_position.maxPlayer:
            return white_squares - black_squares
        else:
            return black_squares - white_squares
