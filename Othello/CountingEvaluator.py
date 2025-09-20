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

    def __init__(self):
        for i in range(1, 9):
            if i != 1 and i != 8:
                self.edges.append((1, i))
                self.edges.append((8, i))
                self.edges.append((i, 1))
                self.edges.append((i, 8))

    def evaluate(self, othello_position: OthelloPosition) -> float:
        weights = {
            "squares": 1,
            "corners": 20,
            "x_squares": -20,
            "c_squares": -15,
            "stable_discs": 10,
            "mobility": 5,
        }
        data = {
            "squares": 0,
            "corners": 0,
            "x_squares": 0,
            "c_squares": 0,
            "middle_squares": 0,
            "stable_discs": 0,
            "mobility": 0,
        }

        white = {key: 0 for key in data.keys()}

        black = {key: 0 for key in data.keys()}

        heuristics = {"W": white, "B": black}

        empty_squares = 0

        total_used_squares = black["squares"] + white["squares"]

        for row, cell_row in enumerate(othello_position.board):
            for col, cell in enumerate(cell_row):
                is_white = cell == "W"
                is_black = cell == "B"
                is_empty = cell == "E"

                if is_white:
                    heuristics["W"]["squares"] += 1
                elif is_black:
                    heuristics["B"]["squares"] += 1
                elif is_empty:
                    empty_squares += 1
                    continue

                if self.is_corner(row, col):
                    heuristics["W" if is_white else "B"]["corners"] += 1
                    heuristics["B" if is_black else "W"]["corners"] += 1

                if self.is_x_squares(row, col):
                    heuristics["W" if is_white else "B"]["x_squares"] += 1
                    heuristics["B" if is_black else "W"]["x_squares"] += 1

                if self.is_c_squares(row, col):
                    heuristics["W" if is_white else "B"]["c_squares"] += 1
                    heuristics["B" if is_black else "W"]["c_squares"] += 1

                if self.is_middle_squares(row, col):
                    heuristics["W" if is_white else "B"]["middle_squares"] += 1
                    heuristics["B" if is_black else "W"]["middle_squares"] += 1

                if self.stable_discs(row, col):
                    heuristics["W" if is_white else "B"]["stable_discs"] += 1
                    heuristics["B" if is_black else "W"]["stable_discs"] += 1

        white_score = sum(weights[key] * heuristics["W"][key] for key in weights.keys())
        black_score = sum(weights[key] * heuristics["B"][key] for key in weights.keys())

        if self.is_early_game(total_used_squares):
            return white_score - black_score

        elif self.is_mid_game(total_used_squares):
            return white_score - black_score

        else:
            return white_score - black_score

    def is_early_game(self, total):
        """
        first 20 moves
        """
        return total < 20

    def is_mid_game(self, total):
        """
        after first 20 moves
        """
        return total < 40

    def is_late_game(self, total):
        """
        last 20 moves
        """
        return not self.is_early_game(total) and not self.is_mid_game(total)

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
        return (row, col) not in (
            self.c_squares + self.x_squares + self.corners + self.edges
        )

    def stable_discs(self,  row, col):
        """
        pieces that cannot be flipped
        """
        pass
