import numpy as np
from OthelloPosition import OthelloPosition


class FeatureExtractor:
    """
    Heuristic feature extractor for Othello positions.

    This class evaluates 10 strategic features from an Othello position for position evaluation.
    Our features are based on established Othello game play principles and are optimized for use
    with numpy arrays for efficient computation.

    All features are calculated from the perspective of the starting player.
    We use zero-indexed arrays for optimization purposes.

    We used numpy for fast arithmetic operations

    Reference:
        DataCamp. (2021, July 2). NumPy Cheat Sheet: Data Analysis in Python. DataCamp. https://www.datacamp.com/cheat-sheet/numpy-cheat-sheet-data-analysis-in-python


    Features extracted:
        - Piece count differences
        - Mobility
        - Strategic square control (corners, edges, X-squares, C-squares)
        - Frontier disc analysis
        - Parity calculations
        - Stability estimation
        - Potential mobility

    Author: Afrasah Benjamin Arko
    """

    def __init__(self, playing_white: bool):
        """
        Initialize the FeatureExtractor with strategic square positions and weights.

        Args:
            playing_white (bool): Determines the perspective for our calculations (True for white, False for black).

        Attributes:
            playing_white (bool): The starting player's color (True for white, False for black).
            corner_positions (np.ndarray): Corner positions on the board (1, 1), (1, 8), (8, 1), (8, 8).
            x_square_positions (np.ndarray): X-square positions, the diagonal squares next to corners.
            c_square_positions (np.ndarray): C-square positions, squares directly beside the corners.
            edge_positions (np.ndarray): Edge positions, squares along the borders but excluding corners.
            feature_names (list): List of feature names for interpretability
        """
        self.playing_white = playing_white

        # Corners (most valuable squares)
        self.corner_positions = np.array([[0, 0], [0, 7], [7, 0], [7, 7]])

        # X-squares (diagonal squares next to corners, highly dangerous)
        self.x_square_positions = np.array([[1, 1], [1, 6], [6, 1], [6, 6]])

        # C-squares (squares directly beside the corners, risky in early game because you risk giving up a corner)
        self.c_square_positions = np.array(
            [
                [0, 1], [0, 6], [1, 0], [1, 7],  # top
                [6, 0], [6, 7], [7, 1], [7, 6],  # bottom
            ]
        )

        # Edge positions (excluding corners)
        edge_positions = []
        for i in range(1, 7):
            edge_positions.extend([[0, i], [7, i], [i, 0], [i, 7]])
        self.edge_positions = np.array(edge_positions)


        # Define 8 directions: N, NE, E, SE, S, SW, W, NW
        self.directions = [
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1),
        ]

        # feature names
        self.feature_names = [
            "piece_diff",
            "mobility_diff",
            "corner_diff",
            "x_square_diff",
            "c_square_diff",
            "edge_diff",
            "frontier_diff",
            "parity_score",
            "stability_diff",
            "potential_mobility_diff",
        ]

    def extract_features(self, position: OthelloPosition) -> np.ndarray:
        """
        Extract a comprehensive feature vector from an Othello position for evaluation.

        This method computes 10 different features that capture various strategic aspects
        of the current board position from the perspective of the starting player.

        Args:
            position (OthelloPosition): The current Othello game position to analyze

        Returns:
            np.ndarray: A 1D numpy array of 10 features with dtype float64:
                [0] piece_diff: Difference in piece count (my_pieces - opp_pieces)
                [1] mobility_diff: Difference in legal moves available
                [2] corner_diff: Difference in corner control
                [3] x_square_diff: Difference in X-square occupation
                [4] c_square_diff: Difference in C-square occupation
                [5] edge_diff: Difference in edge control
                [6] frontier_diff: Difference in frontier discs
                [7] parity_score: Parity advantage based on move tempo
                [8] stability_diff: Difference in disc stability
                [9] potential_mobility_diff: Difference in potential mobility

        Note:
            All differences are calculated from the starting player's perspective.
            Positive values generally favor the starting player.
        """

        features = []

        # use zero-based indexing and exclude the padding - 8x8 np array
        board = position.board[1:9, 1:9].copy()

        # Piece types for current player and opponent
        my_piece = "W" if self.playing_white else "B"
        opp_piece = "B" if self.playing_white else "W"

        # Boolean masks for piece counting
        my_mask = board == my_piece
        opp_mask = board == opp_piece
        empty_mask = board == "E"

        # Count pieces
        my_pieces = np.sum(my_mask)
        opp_pieces = np.sum(opp_mask)
        total_pieces = my_pieces + opp_pieces

        # 1. Piece difference
        features.append(my_pieces - opp_pieces)

        # 2. Mobility difference

        # Get current player's mobility
        my_mobility = len(position.get_moves())
        
        # Get opponent's mobility 
        opponent = position.clone()
        opponent.maxPlayer = not position.maxPlayer
        opp_mobility = len(opponent.get_moves())

        # Calculate mobility difference from starting player's perspective
        if (self.playing_white and position.maxPlayer) or (not self.playing_white and not position.maxPlayer):
            # Starting player is the current player
            mobility_diff = my_mobility - opp_mobility
        else:
            # Starting player is the opponent
            mobility_diff = opp_mobility - my_mobility
            
        features.append(mobility_diff)

        # 3. Corner control difference
        my_corners = np.sum(my_mask[self.corner_positions[:, 0], self.corner_positions[:, 1]])
        opp_corners = np.sum(opp_mask[self.corner_positions[:, 0], self.corner_positions[:, 1]])
        features.append(my_corners - opp_corners)

        # 4. X-square difference (dangerous position for current player, neg is better)
        my_x_squares = np.sum(my_mask[self.x_square_positions[:, 0], self.x_square_positions[:, 1]])
        opp_x_squares = np.sum(opp_mask[self.x_square_positions[:, 0], self.x_square_positions[:, 1]])
        features.append(my_x_squares - opp_x_squares)

        # 5. C-square difference (dangerous position for current player, neg is better)
        my_c_squares = np.sum(my_mask[self.c_square_positions[:, 0], self.c_square_positions[:, 1]])
        opp_c_squares = np.sum(opp_mask[self.c_square_positions[:, 0], self.c_square_positions[:, 1]])
        features.append(my_c_squares - opp_c_squares)

        # 6. Edge control difference
        my_edges = np.sum(my_mask[self.edge_positions[:, 0], self.edge_positions[:, 1]])
        opp_edges = np.sum(opp_mask[self.edge_positions[:, 0], self.edge_positions[:, 1]])
        features.append(my_edges - opp_edges)

        # 7. Frontier discs
        my_frontier = self.__count_frontier_discs(my_mask, empty_mask)
        opp_frontier = self.__count_frontier_discs(opp_mask, empty_mask)
        features.append(my_frontier - opp_frontier)

        # 8. Parity score (we always want to have the last move and reduce our opponent's degree of freedom)
        parity_score = self.__calculate_parity(total_pieces, my_pieces, opp_pieces)
        features.append(parity_score)

        # 9. Stability difference (the higher the better)
        my_stability = self.__estimate_stability(my_mask)
        opp_stability = self.__estimate_stability(opp_mask)
        features.append(my_stability - opp_stability)

        # 10. Potential mobility (empty squares next to opponent)
        my_potential = self.__count_potential_mobility(opp_mask, empty_mask)
        opp_potential = self.__count_potential_mobility(my_mask, empty_mask)
        features.append(my_potential - opp_potential)


        return np.array(features, dtype=np.float64)


    def __count_frontier_discs(self, piece_mask: np.ndarray, empty_mask: np.ndarray) -> int:
        """
        Count frontier discs (pieces adjacent to empty squares).

        Frontier discs are pieces that are adjacent to at least one empty square.
        Having fewer frontier discs is generally advantageous because:
        1. Frontier pieces are more vulnerable to being flipped
        2. They give the opponent more potential moves
        3. They reduce your own mobility

        Args:
            piece_mask (np.ndarray): Boolean 8x8 mask where True indicates pieces of interest
            empty_mask (np.ndarray): Boolean 8x8 mask where True indicates empty squares

        Returns:
            int: Number of frontier discs (pieces adjacent to empty squares)

        Reference:
            Rose, B. (2005). "Othello and A Minute to Learn...A Lifetime to Master."
        """
        # Define 8 directions: N, NE, E, SE, S, SW, W, NW
        directions = [
            (-1, 0),
            (-1, 1),
            (0, 1),
            (1, 1),
            (1, 0),
            (1, -1),
            (0, -1),
            (-1, -1),
        ]

        # Handle boundary checks, no need to worry about indexing out of range.
        padded_empty = np.pad(empty_mask, 1, mode="constant", constant_values=False)

        frontier_mask = np.zeros_like(piece_mask, dtype=bool)

        for dr, dc in directions:
            # Shift the empty mask in the opposite direction to find pieces adjacent to empty squares
            shifted_empty = padded_empty[1 + dr : 9 + dr, 1 + dc : 9 + dc]

            # Mark pieces that are adjacent to empty squares in this direction
            frontier_mask |= piece_mask & shifted_empty

        return np.sum(frontier_mask)

    def __calculate_parity(self, total_pieces: int, my_pieces: int, opp_pieces: int) -> int:
        """
        Calculate parity advantage based on move tempo and endgame positioning.

        PARITY THEORY IN OTHELLO:
        Parity refers to who gets to make the final moves in different regions of the board.
        In Othello endgame, controlling the tempo (when you move) is crucial because:
        1. The last player to move in a region often gains the most discs
        2. You want to force your opponent to move first in unfavorable regions
        3. You want to move last in favorable regions where you can gain many discs

        MATHEMATICAL FOUNDATION:
        - Total remaining moves = 64 - total_pieces
        - If remaining moves is EVEN: both players get equal number of remaining moves
        - If remaining moves is ODD: current player gets one extra move

        STRATEGIC IMPLICATIONS:
        - Even parity (equal moves): Favor the player currently ahead in disc count
        - Odd parity (extra move): Favor the player currently behind (extra move helps catch up)

        Args:
            total_pieces (int): Total number of pieces on the board
            my_pieces (int): Number of pieces for the current player
            opp_pieces (int): Number of pieces for the opponent

        Returns:
            int: Parity score (1 = advantage, 0 = neutral/disadvantage)

        Reference:
            Rose, B. (2005). "Othello and A Minute to Learn...A Lifetime to Master."
        """
        remaining_moves = 64 - total_pieces
        piece_diff = my_pieces - opp_pieces

        # Even number of remaining moves: both players get same number of moves
        if remaining_moves % 2 == 0:
            # When both players get equal moves, being ahead in pieces is advantageous
            # because your lead is likely to be maintained or extended
            if piece_diff >= 0:
                return 1
            else:
                return 0

        # Odd number of remaining moves: current player gets one extra move
        else:
            # When you get an extra move, it's more valuable if you're behind
            # because that extra move can help you catch up or take the lead
            if piece_diff <= 0:
                return 1
            else:
                return 0

    def __estimate_stability(self, piece_mask: np.ndarray) -> int:
        """
        Estimate disc stability using a simplified heuristic approach.

        Stable discs are discs that cannot be flipped in any direction.
        This is a simplified estimation that considers:
        1. Corners are always stable (weighted 3x for importance)
        2. Edges are somewhat stable (weighted 1x)
        3. Interior pieces are assumed neutral (not counted)

        A more sophisticated approach would recursively determine stability
        by checking if pieces are connected to stable pieces in all directions.

        Args:
            piece_mask (np.ndarray): Boolean 8x8 mask where True indicates pieces of interest

        Returns:
            int: Estimated stability score (higher is more stable)

        Reference:
            Rose, B. (2005). "Othello and A Minute to Learn...A Lifetime to Master."
        """

        # Corners are always stable (weight them more heavily)
        corner_count = np.sum(piece_mask[self.corner_positions[:, 0], self.corner_positions[:, 1]])
        stable_count = corner_count * 3

        # Edges are somewhat stable
        edge_count = np.sum(piece_mask[self.edge_positions[:, 0], self.edge_positions[:, 1]])
        stable_count += edge_count

        return stable_count

    def __count_potential_mobility(self, opp_mask: np.ndarray, empty_mask: np.ndarray) -> int:
        """
        Count potential mobility (empty squares adjacent to opponent pieces).

        Potential mobility is the number of empty squares adjacent to opponent pieces.
        It represents the opponent's potential moves even if they're not currently legal.
        Higher potential mobility for the opponent is generally disadvantageous because:
        1. It gives them more future move options
        2. It indicates they have more strategic flexibility
        3. It suggests they may gain mobility as the game progresses

        Args:
            opp_mask (np.ndarray): Boolean 8x8 mask where True indicates opponent pieces
            empty_mask (np.ndarray): Boolean 8x8 mask where True indicates empty squares

        Returns:
            int: Number of empty squares adjacent to opponent pieces

        Reference:
            M. Buro, "An evaluation function for Othello based on statistics,"
            Technical Report, NEC Research Institute, Princeton, NJ, 1995.
        """

        # Handle boundary checks, no need to worry about indexing out of range.
        padded_opp = np.pad(opp_mask, 1, mode="constant", constant_values=False)

        # Track all empty squares adjacent to opponent pieces
        adjacent_empty_mask = np.zeros_like(empty_mask, dtype=bool)

        for dr, dc in self.directions:
            # Shift opponent pieces in each direction to find adjacent empty squares
            shifted_opp = padded_opp[1 + dr : 9 + dr, 1 + dc : 9 + dc]

            # Mark empty squares that are adjacent to opponent pieces
            adjacent_empty_mask |= empty_mask & shifted_opp

        return np.sum(adjacent_empty_mask)