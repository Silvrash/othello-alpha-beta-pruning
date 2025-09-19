from OthelloAction import OthelloAction
from OthelloPosition import OthelloPosition
from OthelloEvaluator import OthelloEvaluator
from itertools import chain

"""
  A simple evaluator that just counts the number of black and white squares 
  Author: Ola Ringdahl
"""


class CountingEvaluator(OthelloEvaluator):
    def __init__(self) -> None:
        super().__init__()
        self.corner_squares = [(1, 1), (1, 8), (8, 1), (8, 8)]
        self.x_squares = [(2, 2), (2, 7), (7, 2), (7, 7)]
        self.c_squares = [
            (1, 2),
            (2, 1),
            (7, 1),
            (8, 2),
            (8, 7),
            (8, 7),
            (1, 7),
            (2, 8),
        ]
        # self.edge_squares = self.__generate_edges()

        # heuristic values
        self.corner_point = 50
        self.stable_point = 40
        self.x_square_point = -200
        self.c_square_point = -10
        self.edge_square_point = 10
        self.middle_square_point = 5
        self.frontier_square_point = 2
        self.single_point = 1

    

    def evaluate(self, othello_position):
        black_squares = 0
        white_squares = 0
        for row in othello_position.board:
            for item in row:
                if item == "W":
                    white_squares += 1
                if item == "B":
                    black_squares += 1
        return white_squares - black_squares
    # def evaluate(self, position: OthelloPosition):
        # WEIGHTS = [
        #     [100, -20, 10, 5, 5, 10, -20, 100],
        #     [-20, -50, -2, -2, -2, -2, -50, -20],
        #     [10, -2, 0, 0, 0, 0, -2, 10],
        #     [5, -2, 0, 0, 0, 0, -2, 5],
        #     [5, -2, 0, 0, 0, 0, -2, 5],
        #     [10, -2, 0, 0, 0, 0, -2, 10],
        #     [-20, -50, -2, -2, -2, -2, -50, -20],
        #     [100, -20, 10, 5, 5, 10, -20, 100],
        # ]
        # my_color = position.maxPlayer
        # opp_color = not my_color
        # board = position.board

        # my_discs, opp_discs = 0, 0
        # pos_score = 0

        # for r in range(8):
        #     for c in range(8):
        #         if board[r][c] == my_color:
        #             my_discs += 1
        #             pos_score += WEIGHTS[r][c]
        #         elif board[r][c] == opp_color:
        #             opp_discs += 1
        #             pos_score -= WEIGHTS[r][c]

        # # Total discs & empties
        # total_discs = my_discs + opp_discs
        # empties = 64 - total_discs

        # # --- Heuristic components ---
        # # Piece difference
        # if total_discs > 0:
        #     disc_diff = 100 * (my_discs - opp_discs) / total_discs
        # else:
        #     disc_diff = 0

        # # Mobility
        # my_moves = len(position.get_moves())
        # opp_moves = len(position.make_move(OthelloAction(0, 0, True)).get_moves())
        # if my_moves + opp_moves > 0:
        #     mobility = 100 * (my_moves - opp_moves) / (my_moves + opp_moves)
        # else:
        #     mobility = 0

        # # Corner control
        # corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        # my_corners = sum(1 for r, c in corners if board[r][c] == my_color)
        # opp_corners = sum(1 for r, c in corners if board[r][c] == opp_color)
        # if my_corners + opp_corners > 0:
        #     corner_control = 100 * (my_corners - opp_corners) / (my_corners + opp_corners)
        # else:
        #     corner_control = 0

        # # --- Phase weighting ---
        # if empties > 40:  # Early game
        #     return (25 * mobility) + (10 * pos_score) + (5 * corner_control)
        # elif empties > 15:  # Midgame
        #     return (30 * mobility) + (15 * pos_score) + (25 * corner_control)
        # else:  # Endgame
        #     return (40 * disc_diff) + (25 * corner_control) + (10 * mobility)