from OthelloEvaluator import OthelloEvaluator

"""
  A simple evaluator that just counts the number of black and white squares 
  Author: Ola Ringdahl
"""


class CountingEvaluator(OthelloEvaluator):
    def evaluate(self, othello_position) -> float:
        black_squares = 0
        white_squares = 0
        for row in othello_position.board:
            for item in row:
                if item == 'W':
                    white_squares += 1
                if item == 'B':
                    black_squares += 1
        # print(f"white_squares: {white_squares}, black_squares: {black_squares}")
        return white_squares - black_squares

    def is_mid_game(self):
        pass

    def is_early_game(self):
        pass

    def is_late_game(self):
        pass