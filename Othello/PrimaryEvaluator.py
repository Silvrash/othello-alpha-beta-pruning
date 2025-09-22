from OthelloAction import OthelloAction
from OthelloPosition import EMPTY_PLACEHOLDER, OthelloPosition
from OthelloEvaluator import OthelloEvaluator
import numpy as np


class PrimaryEvaluator(OthelloEvaluator):
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

    The evaluator uses NumPy operations for efficient calculation
    and pre-computed masks for different position types.

    Author: Afrasah Benjamin Arko & Sienichev Matvey
    """

    DIRECTIONS = [
        (-1, 0),  # Top
        (1, 0),  # Bottom
        (0, 1),  # Right
        (0, -1),  # Left
        (-1, 1),  # Top-right
        (-1, -1),  # Top-left
        (1, 1),  # Bottom-right
        (1, -1),  # Bottom-left
    ]

    def __init__(self):
        """
        Initialize the evaluator with pre-computed position masks.

        Creates boolean masks for different types of board positions:
        - Corner positions (most stable)
        - X-squares (dangerous diagonal positions)
        - C-squares (dangerous adjacent positions)
        - Edge positions (stable border positions)
        - Center positions (4x4 center area)
        """
        # Create all masks for different position types
        (
            self.corner_mask,
            self.x_square_mask,
            self.c_square_mask,
            self.edge_mask,
            self.center_mask,
        ) = np.zeros((5, 8, 8), dtype=bool)

        # Initialize each mask type
        self._setup_corner_mask()
        self._setup_x_square_mask()
        self._setup_c_square_mask()
        self._setup_edge_mask()
        self._setup_center_mask()

    def _setup_corner_mask(self):
        """
        Set up corner position mask.

        Corners are the most stable positions: (1,1), (1,8), (8,1), (8,8)
        These positions can never be flipped once captured.
        """
        self.corner_mask[0, 0] = True  # (1, 1)
        self.corner_mask[0, 7] = True  # (1, 8)
        self.corner_mask[7, 0] = True  # (8, 1)
        self.corner_mask[7, 7] = True  # (8, 8)

    def _setup_x_square_mask(self):
        """
        Set up X-square position mask.

        X-squares are diagonal positions adjacent to corners: (2,2), (2,7), (7,2), (7,7)
        These are extremely dangerous as they often lead to corner loss.
        """
        self.x_square_mask[1, 1] = True  # (2, 2)
        self.x_square_mask[1, 6] = True  # (2, 7)
        self.x_square_mask[6, 1] = True  # (7, 2)
        self.x_square_mask[6, 6] = True  # (7, 7)

    def _setup_c_square_mask(self):
        """
        Set up C-square position mask.

        C-squares are positions directly adjacent to corners:
        (1,2), (2,1), (7,1), (8,2), (8,7), (1,7), (2,8)
        These are dangerous in early game as they risk corner sacrifice.
        """
        self.c_square_mask[0, 1] = True  # (1, 2)
        self.c_square_mask[1, 0] = True  # (2, 1)
        self.c_square_mask[6, 0] = True  # (7, 1)
        self.c_square_mask[7, 1] = True  # (8, 2)
        self.c_square_mask[7, 6] = True  # (8, 7)
        self.c_square_mask[0, 6] = True  # (1, 7)
        self.c_square_mask[1, 7] = True  # (2, 8)

    def _setup_edge_mask(self):
        """
        Set up edge position mask.

        Edge positions are along the board borders but not corners.
        These are more stable than interior positions but less stable than corners.
        """
        # Top edge (row 1, columns 2-7)
        self.edge_mask[0, 1] = True  # (1, 2)
        self.edge_mask[0, 2] = True  # (1, 3)
        self.edge_mask[0, 3] = True  # (1, 4)
        self.edge_mask[0, 4] = True  # (1, 5)
        self.edge_mask[0, 5] = True  # (1, 6)
        self.edge_mask[0, 6] = True  # (1, 7)

        # Bottom edge (row 8, columns 2-7)
        self.edge_mask[7, 1] = True  # (8, 2)
        self.edge_mask[7, 2] = True  # (8, 3)
        self.edge_mask[7, 3] = True  # (8, 4)
        self.edge_mask[7, 4] = True  # (8, 5)
        self.edge_mask[7, 5] = True  # (8, 6)
        self.edge_mask[7, 6] = True  # (8, 7)

        # Left edge (column 1, rows 2-7)
        self.edge_mask[1, 0] = True  # (2, 1)
        self.edge_mask[2, 0] = True  # (3, 1)
        self.edge_mask[3, 0] = True  # (4, 1)
        self.edge_mask[4, 0] = True  # (5, 1)
        self.edge_mask[5, 0] = True  # (6, 1)
        self.edge_mask[6, 0] = True  # (7, 1)

        # Right edge (column 8, rows 2-7)
        self.edge_mask[1, 7] = True  # (2, 8)
        self.edge_mask[2, 7] = True  # (3, 8)
        self.edge_mask[3, 7] = True  # (4, 8)
        self.edge_mask[4, 7] = True  # (5, 8)
        self.edge_mask[5, 7] = True  # (6, 8)
        self.edge_mask[6, 7] = True  # (7, 8)

    def _setup_center_mask(self):
        """
        Set up center control position mask.

        Center positions are the 4x4 area in the middle of the board (rows 3-6, cols 3-6).
        Control of this area provides flexibility and positional advantage.
        """
        # Center 4x4 area: rows 3-6, cols 3-6 (0-indexed: 2-5)
        for row in range(2, 6):
            for col in range(2, 6):
                self.center_mask[row, col] = True

    def evaluate(self, othello_position: OthelloPosition) -> float:
        """
        Evaluate an Othello position using multi-factor heuristics.

        This method implements a sophisticated evaluation system that considers
        multiple factors including stability, positional control, and tactical
        considerations. The evaluation adapts based on the game phase.

        Args:
            othello_position (OthelloPosition): The position to evaluate

        Returns:
            float: Evaluation score (positive favors current player)
        """
        # Define heuristic weights for different factors
        weights = {
            "squares": 1,  # Basic piece count
            "corners": 160,  # Corner control (highest priority)
            "x_squares": -1 / 16,  # X-square avoidance (penalty)
            "c_squares": -1 / 16,  # C-square avoidance (penalty)
            "stable_discs": 16,  # Stable disc count
            "frontier_squares": -1 / 2,  # Frontier avoidance (penalty)
            "mobility": 8,  # Move count advantage
            "edge_squares": 4,  # Edge control
            "center_control": 2,  # Center control
        }

        # heuristic data board for each feature
        data = {
            "squares": 0,
            "corners": 0,
            "x_squares": 0,
            "c_squares": 0,
            "middle_squares": 0,
            "stable_discs": 0,
            "frontier_squares": 0,
            "mobility": 0,
            "edge_squares": 0,
            "center_control": 0,
        }

        # player score board for each feature
        current_player = {key: 0 for key in data.keys()}
        opponent = {key: 0 for key in data.keys()}

        # player symbols
        current_player_symbol = "W" if othello_position.maxPlayer else "B"
        opponent_symbol = "B" if othello_position.maxPlayer else "W"

        heuristics = {current_player_symbol: current_player, opponent_symbol: opponent}

        # compute mobility for current player
        heuristics[current_player_symbol]["mobility"] = self.mobility(othello_position)

        # compute mobility for opponent
        temp_pos = othello_position.clone()
        temp_pos.maxPlayer = not othello_position.maxPlayer
        heuristics[opponent_symbol]["mobility"] = self.mobility(temp_pos)

        # extract playable board area (8x8, convert to 0-based indexing)
        playable_board = othello_position.board[1:9, 1:9]

        # boolean masks for each player
        current_player_mask = playable_board == current_player_symbol
        opponent_mask = playable_board == opponent_symbol
        empty_mask = playable_board == EMPTY_PLACEHOLDER

        # count discs for each player
        heuristics[current_player_symbol]["squares"] = np.sum(current_player_mask)
        heuristics[opponent_symbol]["squares"] = np.sum(opponent_mask)
        empty_squares = np.sum(empty_mask)

        # pre-computed masks for position type counting
        corner_mask_playable = self.corner_mask
        x_square_mask_playable = self.x_square_mask
        c_square_mask_playable = self.c_square_mask
        edge_mask_playable = self.edge_mask
        center_mask_playable = self.center_mask

        # Count different position types using vectorized operations
        heuristics[current_player_symbol]["corners"] = np.sum(
            current_player_mask & corner_mask_playable
        )
        heuristics[opponent_symbol]["corners"] = np.sum(
            opponent_mask & corner_mask_playable
        )

        heuristics[current_player_symbol]["x_squares"] = np.sum(
            current_player_mask & x_square_mask_playable
        )
        heuristics[opponent_symbol]["x_squares"] = np.sum(
            opponent_mask & x_square_mask_playable
        )

        heuristics[current_player_symbol]["c_squares"] = np.sum(
            current_player_mask & c_square_mask_playable
        )
        heuristics[opponent_symbol]["c_squares"] = np.sum(
            opponent_mask & c_square_mask_playable
        )

        heuristics[current_player_symbol]["edge_squares"] = np.sum(
            current_player_mask & edge_mask_playable
        )
        heuristics[opponent_symbol]["edge_squares"] = np.sum(
            opponent_mask & edge_mask_playable
        )

        # count center control
        heuristics[current_player_symbol]["center_control"] = np.sum(
            current_player_mask & center_mask_playable
        )
        heuristics[opponent_symbol]["center_control"] = np.sum(
            opponent_mask & center_mask_playable
        )

        # count middle squares (not corners, edges, x_squares, c_squares, center)
        middle_mask = ~(
            corner_mask_playable
            | x_square_mask_playable
            | c_square_mask_playable
            | edge_mask_playable
            | center_mask_playable
        )
        heuristics[current_player_symbol]["middle_squares"] = np.sum(
            current_player_mask & middle_mask
        )
        heuristics[opponent_symbol]["middle_squares"] = np.sum(
            opponent_mask & middle_mask
        )

        # count frontier squares
        frontier_current = self._count_frontier_squares_vectorized(
            playable_board, current_player_mask, edge_mask_playable
        )
        frontier_opponent = self._count_frontier_squares_vectorized(
            playable_board, opponent_mask, edge_mask_playable
        )
        heuristics[current_player_symbol]["frontier_squares"] = frontier_current
        heuristics[opponent_symbol]["frontier_squares"] = frontier_opponent

        # count stable discs
        stable_current = self._count_stable_discs_vectorized(
            playable_board, current_player_mask
        )
        stable_opponent = self._count_stable_discs_vectorized(
            playable_board, opponent_mask
        )
        heuristics[current_player_symbol]["stable_discs"] = stable_current
        heuristics[opponent_symbol]["stable_discs"] = stable_opponent

        # determine game phase and apply appropriate heuristics
        # total of 64 squares on the board, minus the empty squares
        total_squares = 64 - empty_squares

        if self.is_early_game(total_squares):
            """
            Early game strategy: Focus on mobility, center control, and avoiding traps.
            Prioritize flexibility over immediate piece count.
            """

            heuristics_used = [
                "corners",
                "x_squares",
                "c_squares",
                "stable_discs",
                "frontier_squares",
                "mobility",
                "edge_squares",
                "center_control",
            ]
            current_player_score = sum(
                weights[key] * heuristics[current_player_symbol][key]
                for key in weights.keys()
                if key in heuristics_used
            )
            opponent_score = sum(
                weights[key] * heuristics[opponent_symbol][key]
                for key in weights.keys()
                if key in heuristics_used
            )
            return (
                current_player_score * heuristics[current_player_symbol]["squares"]
                - opponent_score * heuristics[opponent_symbol]["squares"]
            )

        elif self.is_mid_game(total_squares):
            """
            Mid game strategy: Balance all factors with emphasis on stability.
            """
            heuristics_used = [
                "corners",
                "x_squares",
                "c_squares",
                "stable_discs",
                "frontier_squares",
                # "middle_squares",
                "mobility",
                # "edge_squares",
            ]
            current_player_score = sum(
                weights[key] * heuristics[current_player_symbol][key]
                for key in weights.keys()
                if key in heuristics_used
            )
            opponent_score = sum(
                weights[key] * heuristics[opponent_symbol][key]
                for key in weights.keys()
                if key in heuristics_used
            )
            return (
                current_player_score * heuristics[current_player_symbol]["squares"]
                - opponent_score * heuristics[opponent_symbol]["squares"]
            )

        else:
            """
            Late game strategy: Focus on piece count and stability.
            Mobility and center control become less relevant.
            """
            heuristics_used = [
                "corners",
                "x_squares",
                "c_squares",
                "stable_discs",
                "frontier_squares",
                "middle_squares",
                # "mobility",
                # "edge_squares",
                # "center_control",
            ]
            current_player_score = sum(
                weights[key] * heuristics[current_player_symbol][key]
                for key in weights.keys()
                if key in heuristics_used and key != "squares"
            )
            opponent_score = sum(
                weights[key] * heuristics[opponent_symbol][key]
                for key in weights.keys()
                if key in heuristics_used and key != "squares"
            )
            return (
                current_player_score * heuristics[current_player_symbol]["squares"]
                - opponent_score * heuristics[opponent_symbol]["squares"]
            )

    def is_early_game(self, total_squares):
        """
        Determine if the game is in the early phase.

        Early game is defined as the first 15 moves (less than 20 pieces on board).
        In this phase, the focus is on mobility, center control, and avoiding traps.

        Args:
            total_squares (int): Total number of pieces on the board

        Returns:
            bool: True if in early game phase
        """
        return total_squares < 20

    def is_mid_game(self, total):
        """
        Determine if the game is in the mid phase.

        Mid game is defined as moves 15-45 (20-45 pieces on board).
        In this phase, the focus is on balancing all factors with emphasis on stability.

        Args:
            total (int): Total number of pieces on the board

        Returns:
            bool: True if in mid game phase
        """
        return total < 45

    def is_late_game(self, total):
        """
        Determine if the game is in the late phase.

        Late game is defined as the final phase (more than 45 pieces on board).
        In this phase, the focus is on piece count and stability.

        Args:
            total (int): Total number of pieces on the board

        Returns:
            bool: True if in late game phase
        """
        return not self.is_early_game(total) and not self.is_mid_game(total)

    def is_corner(self, row, col):
        """
        corners on the board. once a member is placed at the corner, it can never be flipped
        corners = (1, 1), (1, 8), (8, 1), (8, 8)

        highly advantageous
        """
        return self.corner_mask[row - 1, col - 1]

    def is_x_squares(self, row, col):
        """
        The diagonal squares next to corners.
        This is a dangerous position because if you take those positions before your opponent, it's very easy for
        your opponent to flip them.
        (2, 2), (2, 7), (7, 2), (7, 7)

        highly dangerous
        """
        return self.x_square_mask[row - 1, col - 1]

    def is_c_squares(self, row, col):
        """
        squares directly beside the corners.
        (1, 2), (2, 1), (7, 1), (8, 2), (8, 7), (8, 7), (1, 7), (2, 8)
        In early game, try to avoid them because you risk giving up a corner
        """
        return self.c_square_mask[row - 1, col - 1]

    def is_center_square(self, row, col):
        """
        Check if a position is in the center 4x4 area.
        Center squares: rows 3-6, cols 3-6 (1-indexed)
        """
        return self.center_mask[row - 1, col - 1]

    def is_middle_squares(self, row, col):
        """
        all squares that are not corners, edges, x squares and c squares
        """
        return not (
            self.corner_mask[row - 1, col - 1]
            or self.x_square_mask[row - 1, col - 1]
            or self.c_square_mask[row - 1, col - 1]
            or self.edge_mask[row - 1, col - 1]
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
        return self.edge_mask[row - 1, col - 1]

    def is_stable_discs(self, row, col, board):
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

    def _count_frontier_squares_vectorized(
        self, playable_board, player_mask, edge_mask
    ):
        """
        Vectorized frontier squares detection.
        Frontier squares are squares that border with one or more empty squares, excluding edge squares.
        """
        frontier_count = 0
        empty_mask = playable_board == EMPTY_PLACEHOLDER

        # Get positions of player pieces that are not on edges
        player_positions = np.where(player_mask & ~edge_mask)

        for i in range(len(player_positions[0])):
            row, col = player_positions[0][i], player_positions[1][i]

            # Check all 8 directions for empty squares
            for dr, dc in self.DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if (
                    0 <= new_row < 8
                    and 0 <= new_col < 8
                    and empty_mask[new_row, new_col]
                ):
                    frontier_count += 1
                    break  # Found at least one empty neighbor, this is a frontier square

        return frontier_count

    def _count_stable_discs_vectorized(self, playable_board, player_mask):
        """
        Optimized stable discs detection.
        A disc is stable if it cannot be flipped in any direction.
        """
        stable_count = 0
        player_positions = np.where(player_mask)

        for i in range(len(player_positions[0])):
            row, col = player_positions[0][i], player_positions[1][i]
            color = playable_board[row, col]
            is_stable = True

            # Check stability in all 8 directions
            for dr, dc in self.DIRECTIONS:
                r, c = row, col
                stable_in_direction = False

                # Walk along this direction until hitting the board boundary
                while 0 <= r < 8 and 0 <= c < 8:
                    if playable_board[r, c] != color:
                        # Hit opponent or empty → not stable in this direction
                        stable_in_direction = False
                        break
                    r += dr
                    c += dc

                # If we exited loop by crossing the board boundary → stable direction
                if not (0 <= r < 8 and 0 <= c < 8):
                    stable_in_direction = True

                if not stable_in_direction:
                    is_stable = False
                    break

            if is_stable:
                stable_count += 1

        return stable_count

    def mobility(self, position: OthelloPosition):
        """
        Calculate the mobility (number of legal moves) for the current player.

        Mobility is a key tactical factor - having more legal moves provides
        more options and flexibility. It's particularly important in early
        and mid game phases.

        Args:
            position (OthelloPosition): The position to evaluate

        Returns:
            int: Number of legal moves for the current player
        """
        return len(position.get_moves())

    def move_priority(self, action: OthelloAction):
        """
        Calculate move priority for move ordering optimization.

        This method assigns priority values to moves to improve alpha-beta
        pruning efficiency. Higher priority moves are searched first,
        increasing the likelihood of early cutoffs.

        Priority order (highest to lowest):
        1. Corner moves (1000) - Most stable
        2. Edge moves (100) - Stable
        3. Center moves (10) - Good for early game
        4. Regular moves (1) - Neutral
        5. C-square moves (-500) - Dangerous
        6. X-square moves (-1000) - Most dangerous
        7. Pass moves (-∞) - Only when forced

        Args:
            action (OthelloAction): The move to evaluate

        Returns:
            float: Priority value for move ordering
        """
        # Pass moves get lowest priority
        if action.is_pass_move:
            return float("-inf")

        # Convert 1-indexed coordinates to 0-indexed for mask lookup
        row_idx = action.row - 1
        col_idx = action.col - 1

        # Corner moves get highest priority
        # our heuristic focuses on stability, gaining a corner increases
        # your chances of getting more stable discs
        if self.corner_mask[row_idx, col_idx]:
            return 1000

        # X squares get lowest priority
        # X squares increases the likelihood of losing a corner
        # Classified as the most dangerous squares
        elif self.x_square_mask[row_idx, col_idx]:
            return -1000

        # C squares get lowest priority
        # C squares increases the likelihood of losing a corner
        # Classified as dangerous
        elif self.c_square_mask[row_idx, col_idx]:
            return -500

        # Edge moves get medium priority
        # edges are not as stable as corners, but they are still advantageous
        elif self.edge_mask[row_idx, col_idx]:
            return 100

        # Center moves get lower priority
        # centers are not as stable as corners or edges, but they are still advantageous
        # and play a significant role in the early game
        elif self.center_mask[row_idx, col_idx]:
            return 10

        # every other square gets the same priority
        else:
            return 1
