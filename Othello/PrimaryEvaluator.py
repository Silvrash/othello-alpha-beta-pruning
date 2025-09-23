from OthelloAction import OthelloAction
from BitboardOthelloPosition import BitboardOthelloPosition
from OthelloEvaluator import OthelloEvaluator


class PrimaryEvaluator(OthelloEvaluator):
    """
    Optimized bitboard-based heuristic evaluator for Othello positions.

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

    The evaluator uses bitboard operations for maximum performance
    and pre-computed bitboard masks for different position types.

    ONLY supports BitboardOthelloPosition for optimal performance.

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

        Creates bitboard masks for different types of board positions:
        - Corner positions (most stable)
        - X-squares (dangerous diagonal positions)
        - C-squares (dangerous adjacent positions)
        - Edge positions (stable border positions)
        - Center positions (4x4 center area)
        
        Each mask is a 64-bit integer where bit positions correspond to:
        Bit 0 = (0,0), Bit 1 = (0,1), ..., Bit 7 = (0,7)
        Bit 8 = (1,0), Bit 9 = (1,1), ..., Bit 15 = (1,7)
        ...
        Bit 56 = (7,0), Bit 57 = (7,1), ..., Bit 63 = (7,7)
        """
        # Create all masks for different position types as bitboards
        self.corner_mask = 0
        self.x_square_mask = 0
        self.c_square_mask = 0
        self.edge_mask = 0
        self.center_mask = 0

        # Initialize each mask type
        self._setup_corner_mask()
        self._setup_x_square_mask()
        self._setup_c_square_mask()
        self._setup_edge_mask()
        self._setup_center_mask()

    def _setup_corner_mask(self):
        """
        Set up corner position bitboard mask.

        Corners are the most stable positions: (0,0), (0,7), (7,0), (7,7)
        These positions can never be flipped once captured.
        """
        # Corner bit positions: (0,0)=0, (0,7)=7, (7,0)=56, (7,7)=63
        self.corner_mask = (1 << 0) | (1 << 7) | (1 << 56) | (1 << 63)

    def _setup_x_square_mask(self):
        """
        Set up X-square position bitboard mask.

        X-squares are diagonal positions adjacent to corners: (1,1), (1,6), (6,1), (6,6)
        These are extremely dangerous as they often lead to corner loss.
        """
        # X-square bit positions: (1,1)=9, (1,6)=14, (6,1)=49, (6,6)=54
        self.x_square_mask = (1 << 9) | (1 << 14) | (1 << 49) | (1 << 54)

    def _setup_c_square_mask(self):
        """
        Set up C-square position bitboard mask.

        C-squares are positions directly adjacent to corners:
        (0,1), (1,0), (6,0), (7,1), (7,6), (0,6), (1,7)
        These are dangerous in early game as they risk corner sacrifice.
        """
        # C-square bit positions: (0,1)=1, (1,0)=8, (6,0)=48, (7,1)=57, (7,6)=62, (0,6)=6, (1,7)=15
        self.c_square_mask = (1 << 1) | (1 << 8) | (1 << 48) | (1 << 57) | (1 << 62) | (1 << 6) | (1 << 15)

    def _setup_edge_mask(self):
        """
        Set up edge position bitboard mask.

        Edge positions are along the board borders but not corners.
        These are more stable than interior positions but less stable than corners.
        """
        # Top edge (row 0, columns 1-6): bits 1-6
        # Bottom edge (row 7, columns 1-6): bits 57-62
        # Left edge (column 0, rows 1-6): bits 8,16,24,32,40,48
        # Right edge (column 7, rows 1-6): bits 15,23,31,39,47,55
        
        self.edge_mask = (
            # Top edge: (0,1)=1, (0,2)=2, (0,3)=3, (0,4)=4, (0,5)=5, (0,6)=6
            (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6) |
            # Bottom edge: (7,1)=57, (7,2)=58, (7,3)=59, (7,4)=60, (7,5)=61, (7,6)=62
            (1 << 57) | (1 << 58) | (1 << 59) | (1 << 60) | (1 << 61) | (1 << 62) |
            # Left edge: (1,0)=8, (2,0)=16, (3,0)=24, (4,0)=32, (5,0)=40, (6,0)=48
            (1 << 8) | (1 << 16) | (1 << 24) | (1 << 32) | (1 << 40) | (1 << 48) |
            # Right edge: (1,7)=15, (2,7)=23, (3,7)=31, (4,7)=39, (5,7)=47, (6,7)=55
            (1 << 15) | (1 << 23) | (1 << 31) | (1 << 39) | (1 << 47) | (1 << 55)
        )

    def _setup_center_mask(self):
        """
        Set up center control position bitboard mask.

        Center positions are the 4x4 area in the middle of the board (rows 2-5, cols 2-5).
        Control of this area provides flexibility and positional advantage.
        """
        # Center 4x4 area: rows 2-5, cols 2-5 (0-indexed)
        # Bit positions: (2,2)=18, (2,3)=19, (2,4)=20, (2,5)=21
        #               (3,2)=26, (3,3)=27, (3,4)=28, (3,5)=29
        #               (4,2)=34, (4,3)=35, (4,4)=36, (4,5)=37
        #               (5,2)=42, (5,3)=43, (5,4)=44, (5,5)=45
        self.center_mask = (
            (1 << 18) | (1 << 19) | (1 << 20) | (1 << 21) |
            (1 << 26) | (1 << 27) | (1 << 28) | (1 << 29) |
            (1 << 34) | (1 << 35) | (1 << 36) | (1 << 37) |
            (1 << 42) | (1 << 43) | (1 << 44) | (1 << 45)
        )

    def evaluate(self, othello_position: BitboardOthelloPosition, action) -> float:
        """
        Evaluate a BitboardOthelloPosition using optimized bitboard operations.

        This method implements a sophisticated evaluation system that considers
        multiple factors including stability, positional control, and tactical
        considerations. The evaluation adapts based on the game phase.

        Args:
            othello_position (BitboardOthelloPosition): The bitboard position to evaluate

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

        # Get bitboards for current player and opponent
        if othello_position.maxPlayer:
            my_bitboard = othello_position.white_bitboard
            opp_bitboard = othello_position.black_bitboard
        else:
            my_bitboard = othello_position.black_bitboard
            opp_bitboard = othello_position.white_bitboard

        # Count pieces using bitboard operations
        my_squares = bin(my_bitboard).count('1')
        opp_squares = bin(opp_bitboard).count('1')
        total_squares = my_squares + opp_squares

        # Initialize heuristic scores
        my_score = 0
        opp_score = 0

        # Count different position types using bitboard operations
        my_corners = bin(my_bitboard & self.corner_mask).count('1')
        opp_corners = bin(opp_bitboard & self.corner_mask).count('1')

        my_x_squares = bin(my_bitboard & self.x_square_mask).count('1')
        opp_x_squares = bin(opp_bitboard & self.x_square_mask).count('1')

        my_c_squares = bin(my_bitboard & self.c_square_mask).count('1')
        opp_c_squares = bin(opp_bitboard & self.c_square_mask).count('1')

        my_edge_squares = bin(my_bitboard & self.edge_mask).count('1')
        opp_edge_squares = bin(opp_bitboard & self.edge_mask).count('1')

        my_center_squares = bin(my_bitboard & self.center_mask).count('1')
        opp_center_squares = bin(opp_bitboard & self.center_mask).count('1')

        # Calculate middle squares (not corners, edges, x_squares, c_squares, center)
        special_positions_mask = (self.corner_mask | self.x_square_mask | 
                                 self.c_square_mask | self.edge_mask | self.center_mask)
        my_middle_squares = bin(my_bitboard & ~special_positions_mask).count('1')
        opp_middle_squares = bin(opp_bitboard & ~special_positions_mask).count('1')

        # Calculate mobility
        my_mobility = len(othello_position.get_moves())
        temp_pos = othello_position.clone()
        temp_pos.maxPlayer = not othello_position.maxPlayer
        opp_mobility = len(temp_pos.get_moves())

        # Calculate frontier squares (pieces adjacent to empty squares, excluding edges)
        my_frontier = self._count_frontier_squares_bitboard(my_bitboard, othello_position.empty_bitboard)
        opp_frontier = self._count_frontier_squares_bitboard(opp_bitboard, othello_position.empty_bitboard)

        # Calculate stable discs
        my_stable = self._count_stable_discs_bitboard(my_bitboard, opp_bitboard)
        opp_stable = self._count_stable_discs_bitboard(opp_bitboard, my_bitboard)

        # Determine game phase and apply appropriate heuristics
        if self.is_early_game(total_squares):
            # Early game strategy: Focus on mobility, center control, and avoiding traps
            my_score = (
                weights["corners"] * my_corners +
                weights["x_squares"] * my_x_squares +
                weights["c_squares"] * my_c_squares +
                weights["stable_discs"] * my_stable +
                weights["frontier_squares"] * my_frontier +
                weights["mobility"] * my_mobility +
                weights["edge_squares"] * my_edge_squares +
                weights["center_control"] * my_center_squares
            )
            opp_score = (
                weights["corners"] * opp_corners +
                weights["x_squares"] * opp_x_squares +
                weights["c_squares"] * opp_c_squares +
                weights["stable_discs"] * opp_stable +
                weights["frontier_squares"] * opp_frontier +
                weights["mobility"] * opp_mobility +
                weights["edge_squares"] * opp_edge_squares +
                weights["center_control"] * opp_center_squares
            )
            return (my_score * my_squares) - (opp_score * opp_squares)

        elif self.is_mid_game(total_squares):
            # Mid game strategy: Balance all factors with emphasis on stability
            my_score = (
                weights["corners"] * my_corners +
                weights["x_squares"] * my_x_squares +
                weights["c_squares"] * my_c_squares +
                weights["stable_discs"] * my_stable +
                weights["frontier_squares"] * my_frontier +
                weights["mobility"] * my_mobility
            )
            opp_score = (
                weights["corners"] * opp_corners +
                weights["x_squares"] * opp_x_squares +
                weights["c_squares"] * opp_c_squares +
                weights["stable_discs"] * opp_stable +
                weights["frontier_squares"] * opp_frontier +
                weights["mobility"] * opp_mobility
            )
            return (my_score * my_squares) - (opp_score * opp_squares)

        else:
            # Late game strategy: Focus on piece count and stability
            my_score = (
                weights["corners"] * my_corners +
                weights["x_squares"] * my_x_squares +
                weights["c_squares"] * my_c_squares +
                weights["stable_discs"] * my_stable +
                weights["frontier_squares"] * my_frontier +
                weights["squares"] * my_middle_squares
            )
            opp_score = (
                weights["corners"] * opp_corners +
                weights["x_squares"] * opp_x_squares +
                weights["c_squares"] * opp_c_squares +
                weights["stable_discs"] * opp_stable +
                weights["frontier_squares"] * opp_frontier +
                weights["squares"] * opp_middle_squares
            )
            return (my_score * my_squares) - (opp_score * opp_squares)

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
        # Convert 1-indexed to 0-indexed and calculate bit position
        bit_pos = (row - 1) * 8 + (col - 1)
        return bool(self.corner_mask & (1 << bit_pos))

    def is_x_squares(self, row, col):
        """
        The diagonal squares next to corners.
        This is a dangerous position because if you take those positions before your opponent, it's very easy for
        your opponent to flip them.
        (2, 2), (2, 7), (7, 2), (7, 7)

        highly dangerous
        """
        # Convert 1-indexed to 0-indexed and calculate bit position
        bit_pos = (row - 1) * 8 + (col - 1)
        return bool(self.x_square_mask & (1 << bit_pos))

    def is_c_squares(self, row, col):
        """
        squares directly beside the corners.
        (1, 2), (2, 1), (7, 1), (8, 2), (8, 7), (8, 7), (1, 7), (2, 8)
        In early game, try to avoid them because you risk giving up a corner
        """
        # Convert 1-indexed to 0-indexed and calculate bit position
        bit_pos = (row - 1) * 8 + (col - 1)
        return bool(self.c_square_mask & (1 << bit_pos))

    def is_center_square(self, row, col):
        """
        Check if a position is in the center 4x4 area.
        Center squares: rows 3-6, cols 3-6 (1-indexed)
        """
        # Convert 1-indexed to 0-indexed and calculate bit position
        bit_pos = (row - 1) * 8 + (col - 1)
        return bool(self.center_mask & (1 << bit_pos))

    def is_middle_squares(self, row, col):
        """
        all squares that are not corners, edges, x squares and c squares
        """
        # Convert 1-indexed to 0-indexed and calculate bit position
        bit_pos = (row - 1) * 8 + (col - 1)
        return not (
            (self.corner_mask & (1 << bit_pos)) or
            (self.x_square_mask & (1 << bit_pos)) or
            (self.c_square_mask & (1 << bit_pos)) or
            (self.edge_mask & (1 << bit_pos))
        )

    def is_frontier_squares(self, row, col, bitboard_position):
        """
        Check if a square borders with one or more empty squares, excluding edge squares.
        Uses bitboard operations for efficiency.
        """
        if self.is_edge_squares(row, col):
            return False
        
        # Check all 8 directions for empty squares
        for dr, dc in self.DIRECTIONS:
            new_row, new_col = row - 1 + dr, col - 1 + dc  # Convert to 0-indexed
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                new_bit_pos = new_row * 8 + new_col
                if bitboard_position.empty_bitboard & (1 << new_bit_pos):
                    return True
        return False

    def is_edge_squares(self, row, col):
        """
        squares along the borders but not corners
        """
        # Convert 1-indexed to 0-indexed and calculate bit position
        bit_pos = (row - 1) * 8 + (col - 1)
        return bool(self.edge_mask & (1 << bit_pos))

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


    def _count_frontier_squares_bitboard(self, player_bitboard, empty_bitboard):
        """
        Count frontier squares using bitboard operations.
        Frontier squares are player pieces adjacent to empty squares, excluding edge pieces.
        """
        frontier_count = 0
        
        # Remove edge pieces from consideration
        non_edge_player_pieces = player_bitboard & ~self.edge_mask
        
        # For each non-edge player piece, check if it's adjacent to an empty square
        temp_pieces = non_edge_player_pieces
        while temp_pieces:
            # Get the rightmost set bit
            piece_bit = temp_pieces & -temp_pieces
            piece_pos = piece_bit.bit_length() - 1
            
            # Convert bit position to row, col
            row, col = piece_pos // 8, piece_pos % 8
            
            # Check all 8 directions for empty squares
            is_frontier = False
            for dr, dc in self.DIRECTIONS:
                new_row, new_col = row + dr, col + dc
                if 0 <= new_row < 8 and 0 <= new_col < 8:
                    new_bit_pos = new_row * 8 + new_col
                    if empty_bitboard & (1 << new_bit_pos):
                        is_frontier = True
                        break
            
            if is_frontier:
                frontier_count += 1
                
            # Remove this piece from consideration
            temp_pieces &= temp_pieces - 1
            
        return frontier_count

    def _count_stable_discs_bitboard(self, my_bitboard, opp_bitboard):
        """
        Count stable discs using bitboard operations.
        A disc is stable if it cannot be flipped in any direction.
        """
        stable_count = 0
        temp_pieces = my_bitboard
        
        while temp_pieces:
            # Get the rightmost set bit
            piece_bit = temp_pieces & -temp_pieces
            piece_pos = piece_bit.bit_length() - 1
            
            # Convert bit position to row, col
            row, col = piece_pos // 8, piece_pos % 8
            
            # Check if this piece is stable in all directions
            is_stable = True
            for dr, dc in self.DIRECTIONS:
                stable_in_direction = False
                r, c = row, col
                
                # Walk along this direction until hitting the board boundary
                while 0 <= r < 8 and 0 <= c < 8:
                    bit_pos = r * 8 + c
                    # If we hit opponent or empty square, not stable in this direction
                    if (opp_bitboard & (1 << bit_pos)) or not ((my_bitboard | opp_bitboard) & (1 << bit_pos)):
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
                
            # Remove this piece from consideration
            temp_pieces &= temp_pieces - 1
            
        return stable_count

    def mobility(self, position: BitboardOthelloPosition):
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

        # Convert 1-indexed coordinates to 0-indexed and calculate bit position
        row_idx = action.row - 1
        col_idx = action.col - 1
        bit_pos = row_idx * 8 + col_idx

        # Corner moves get highest priority
        # our heuristic focuses on stability, gaining a corner increases
        # your chances of getting more stable discs
        if self.corner_mask & (1 << bit_pos):
            return 1000

        # X squares get lowest priority
        # X squares increases the likelihood of losing a corner
        # Classified as the most dangerous squares
        elif self.x_square_mask & (1 << bit_pos):
            return -1000

        # C squares get low priority
        # C squares increases the likelihood of losing a corner
        # Classified as dangerous
        elif self.c_square_mask & (1 << bit_pos):
            return -500

        # Edge moves get medium priority
        # edges are not as stable as corners, but they are still advantageous
        elif self.edge_mask & (1 << bit_pos):
            return 100

        # Center moves get lower priority
        # centers are not as stable as corners or edges, but they are still advantageous
        # and play a significant role in the early game
        elif self.center_mask & (1 << bit_pos):
            return 10

        # every other square gets the same priority
        else:
            return 1
