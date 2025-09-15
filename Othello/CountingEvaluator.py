from OthelloPosition import OthelloPosition
from OthelloEvaluator import OthelloEvaluator

"""
  A simple evaluator that just counts the number of black and white squares 
  Author: Ola Ringdahl
"""


class CountingEvaluator(OthelloEvaluator):
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    x_squares = [(2, 2), (2, 7), (7, 2), (7, 7)]
    c_squares = [(1, 2), (2, 1), (7, 1), (8, 2), (8, 7), (8, 7), (1, 7), (2, 8)]
    edges = []



    def evaluate(self, othello_position: OthelloPosition) -> float:
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

    def is_early_game(self):
        """
        first 20 moves
        """
        pass


    def is_mid_game(self):
        """
        after first 20 moves
        """
        pass



    def is_late_game(self):
        """
        last 20 moves
        """
        pass

    def number_at_edges(self):
        """
        squares along the borders but not corners
        row 1 minus (1,1) and (1, 8)
        row 8 minus (8, 1) and (8, 8)
        col 1 minus (1, 1) and (8, 1)
        col 8 minus (1, 8) and (8, 8)

        advantageous
        """
        pass

    def is_corner(self, row, col):
        """
        corners on the board. once a member is placed at the corner, it can never be flipped
        corners = (1, 1), (1, 8), (8, 1), (8, 8)

        highly advantageous
        """
        
        return (row, col) in self.corners

    def is_x_squares(self, row, col):
        """
        The diagonal squares next to corners.
        This is a dangerous position because if you take those positions before your opponent, it's very easy for
        your opponent to flip them.
        (2, 2), (2, 7), (7, 2), (7, 7)

        highly dangerous
        """
        return (row, col) in self.x_squares

    def is_c_squares(self, row, col):
        """
        squares directly beside the corners.
        (1, 2), (2, 1), (7, 1), (8, 2), (8, 7), (8, 7), (1, 7), (2, 8)
        In early game, try to avoid them because you risk giving up a corner
        """
        return (row, col) in self.c_squares

    def is_middle_squares(self, row, col):
        """
        all squares that are not corners, edges, x squares and c squares
        """
        return (row, col) not in (self.c_squares + self.x_squares + self.corners + self.edges)

    def stable_discs(self):
        """
        pieces that cannot be flipped
        """
        pass