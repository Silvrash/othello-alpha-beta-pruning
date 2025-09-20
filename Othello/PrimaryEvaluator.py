from OthelloAction import OthelloAction
from OthelloPosition import EMPTY_PLACEHOLDER, OthelloPosition
from OthelloEvaluator import OthelloEvaluator

"""
  A simple evaluator that just counts the number of black and white squares 
  Author: Ola Ringdahl
"""


class PrimaryEvaluator(OthelloEvaluator):
    corners = [(1, 1), (1, 8), (8, 1), (8, 8)]
    x_squares = [(2, 2), (2, 7), (7, 2), (7, 7)]
    c_squares = [(1, 2), (2, 1), (7, 1), (8, 2), (8, 7), (8, 7), (1, 7), (2, 8)]
    edges = []

    DIRECTIONS = [
            (-1, 0),
            (1, 0),
            (0, 1),
            (0, -1),
            (-1, 1),
            (-1, -1),
            (1, 1),
            (1, -1),
        ]

    def __init__(self):
        for i in range(1, 9):
            if i != 1 and i != 8:
                self.edges.append((1, i))
                self.edges.append((8, i))
                self.edges.append((i, 1))
                self.edges.append((i, 8))

    def evaluate(self, othello_position: OthelloPosition) -> float:
        weights = {
            "squares": 4,
            "corners": 50,
            "x_squares": -20,
            "c_squares": -15,
            "stable_discs": 15,
            "frontier_squares": -5,
            "mobility": 15,
            "edge_squares":10,
        }
        data = {
            "squares": 0,
            "corners": 0,
            "x_squares": 0,
            "c_squares": 0,
            "middle_squares": 0,
            "stable_discs": 0,
            "frontier_squares": 0,
            "mobility": 1,
            "edge_squares": 0,
        }

        current_player = {key: 0 for key in data.keys()}

        opponent = {key: 0 for key in data.keys()}

        current_player_symbol = "W" if othello_position.maxPlayer else "B"
        opponent_symbol = "B" if othello_position.maxPlayer else "W"

        heuristics = {current_player_symbol: current_player, opponent_symbol: opponent}

        heuristics[current_player_symbol]["mobility"] = self.mobility(othello_position)

        # Calculate opponent's mobility by creating a temporary position with opponent as current player
        temp_pos = othello_position.clone()
        temp_pos.maxPlayer = not othello_position.maxPlayer
        heuristics[opponent_symbol]["mobility"] = self.mobility(temp_pos)

        empty_squares = 0

        for row in range(1, 9):
            row_cells = othello_position.board[row]
            for col in range(1, 9):
                cell = row_cells[col]
                is_current_player_disc = cell == current_player_symbol
                is_opponent_disc = cell == opponent_symbol
                player_symbol = current_player_symbol if is_current_player_disc else opponent_symbol if is_opponent_disc else None

                if player_symbol:
                    heuristics[player_symbol]["squares"] += 1
                else:
                    empty_squares += 1
                    continue

                if self.is_corner(row, col):
                    heuristics[player_symbol]["corners"] += 1

                if self.is_x_squares(row, col):
                    heuristics[player_symbol]["x_squares"] += 1

                if self.is_c_squares(row, col):
                    heuristics[player_symbol]["c_squares"] += 1

                if self.is_middle_squares(row, col):
                    heuristics[player_symbol]["middle_squares"] += 1

                if self.is_stable_discs(row, col, othello_position.board):
                    heuristics[player_symbol]["stable_discs"] += 1

                if self.is_edge_squares(row, col):
                    heuristics[player_symbol]["edge_squares"] += 1

                if self.is_frontier_squares(row, col, othello_position.board):
                    heuristics[player_symbol]["frontier_squares"] += 1

        total_squares = 64 - empty_squares
        if self.is_early_game(total_squares):
            '''
            in early game, we want to maximize the number of corners and mobility and minimize the number of x squares and c squares
            '''
            heuristics_used = [
                "corners",
                "mobility",
                "x_squares",
                "c_squares",
                "frontier_squares",
                "squares",
            ]
            current_player_score = sum(weights[key] * heuristics[current_player_symbol][key] for key in weights.keys() if key in heuristics_used)
            opponent_score = sum(weights[key] * heuristics[opponent_symbol][key] for key in weights.keys() if key in heuristics_used)
            return current_player_score - opponent_score

        elif self.is_mid_game(total_squares):
            '''
            in mid game, we want to maximize the number of corners, and stable discs
            '''
            heuristics_used = [
                "corners",
                "stable_discs",
                "edge_squares",
                "mobility",
                "squares",
            ]
            current_player_score = sum(weights[key] * heuristics[current_player_symbol][key] for key in weights.keys() if key in heuristics_used)
            opponent_score = sum(weights[key] * heuristics[opponent_symbol][key] for key in weights.keys() if key in heuristics_used)
            return current_player_score - opponent_score

        else:
            '''
            in late game, we want to maximize the number of discs
            '''
            heuristics_used = ["corners", "squares", "stable_discs", "mobility", 'edge_squares']
            current_player_score = sum(weights[key] * heuristics[current_player_symbol][key] for key in weights.keys() if key in heuristics_used)
            opponent_score = sum(weights[key] * heuristics[opponent_symbol][key] for key in weights.keys() if key in heuristics_used)
            return current_player_score - opponent_score

    def is_early_game(self, total):
        """
        first 15 moves
        """
        return total < 15

    def is_mid_game(self, total):
        """
        after first 15 moves to 45 moves
        """
        return total < 45

    def is_late_game(self, total):
        """
        last 15 moves
        """
        return not self.is_early_game(total) and not self.is_mid_game(total)


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

    def is_frontier_squares(self, row, col, board):
        """
        squares that border with one or more empty squares
        excluding edge squares
        """

        if self.is_edge_squares(row, col):
            return False

        for dr, dc in self.DIRECTIONS:
            if board[row + dr][col + dc] == EMPTY_PLACEHOLDER:
                return True
        return False

    def is_edge_squares(self, row, col):
        """
        squares along the borders but not corners
        """
        return (row, col) in self.edges

    def is_stable_discs(self,  row, col, board):
        """
        pieces that cannot be flipped
        Returns True if stable, False otherwise.
        """
        
        color = board[row, col]
        for dr, dc in self.DIRECTIONS:
            r, c = row, col
            stable_dir = False

            # Walk along this direction until hitting the 10x10 border
            while 1 <= r <= 8 and 1 <= c <= 8:
                if board[r, c] != color:
                    # Hit opponent or empty → not stable in this direction
                    stable_dir = False
                    break
                r += dr
                c += dc

            # If we exited loop by crossing the playable area boundary → stable direction
            if not (1 <= r <= 8 and 1 <= c <= 8):
                stable_dir = True

            if not stable_dir:
                return False

        return True

    def mobility(self, position: OthelloPosition):
        """
        number of legal moves for the player
        """
        return len(position.get_moves())
