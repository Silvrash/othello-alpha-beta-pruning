from __future__ import annotations
from OthelloAction import OthelloAction


class OptimizedBitboardPosition(object):
    """
    Ultra-fast bitboard Othello implementation optimized for deep search.
    
    Key optimizations:
    1. O(1) move generation using bitboard shifts
    2. O(1) move making using parallel bitboard flipping
    3. Minimal object creation and copying
    4. Precomputed direction masks and shift amounts
    
    This should achieve 10x+ speedup over the original bitboard implementation.
    """

    def __init__(self, board_str=""):
        """Initialize position from board string or empty board."""
        self.BOARD_SIZE = 8
        self.maxPlayer = True  # True = White to move, False = Black to move
        
        # Initialize bitboards
        self.white_bitboard = 0
        self.black_bitboard = 0
        self.empty_bitboard = 0xFFFFFFFFFFFFFFFF  # All squares empty initially
        
        # Precomputed masks for edge detection (prevents bit shifts from wrapping)
        self.NOT_A_FILE = 0xFEFEFEFEFEFEFEFE  # ~column A
        self.NOT_H_FILE = 0x7F7F7F7F7F7F7F7F  # ~column H
        self.NOT_AB_FILE = 0xFCFCFCFCFCFCFCFC  # ~columns A,B
        self.NOT_GH_FILE = 0x3F3F3F3F3F3F3F3F  # ~columns G,H
        
        if len(board_str) >= 65:
            # Set player to move
            self.maxPlayer = board_str[0] == "W"
            
            # Parse board string into bitboards
            for i in range(1, min(65, len(board_str))):
                bit_pos = i - 1  # Convert 1-based to 0-based
                if bit_pos >= 64:
                    break
                    
                if board_str[i] == "O":  # White piece
                    self.white_bitboard |= (1 << bit_pos)
                    self.empty_bitboard &= ~(1 << bit_pos)
                elif board_str[i] == "X":  # Black piece
                    self.black_bitboard |= (1 << bit_pos)
                    self.empty_bitboard &= ~(1 << bit_pos)

    def initialize(self):
        """Initialize the position by placing four coins in the middle of the board"""
        # Clear all bitboards
        self.white_bitboard = 0
        self.black_bitboard = 0
        self.empty_bitboard = 0xFFFFFFFFFFFFFFFF
        
        # Place initial pieces (middle 4 squares)
        # (3,3) = bit 27, (3,4) = bit 28, (4,3) = bit 35, (4,4) = bit 36
        self.white_bitboard = (1 << 27) | (1 << 36)  # White pieces
        self.black_bitboard = (1 << 28) | (1 << 35)  # Black pieces
        
        # Update empty bitboard
        self.empty_bitboard = 0xFFFFFFFFFFFFFFFF & ~(self.white_bitboard | self.black_bitboard)
        self.maxPlayer = True

    def get_moves(self) -> list[OthelloAction]:
        """
        Ultra-fast move generation using bitboard operations.
        Uses parallel bitboard shifts to generate all moves at once.
        """
        if self.maxPlayer:
            my_pieces = self.white_bitboard
            opp_pieces = self.black_bitboard
        else:
            my_pieces = self.black_bitboard
            opp_pieces = self.white_bitboard
        
        # Generate all possible moves using bitboard magic
        possible_moves = self._generate_moves_bitboard(my_pieces, opp_pieces)
        
        # Convert bitboard to list of actions
        moves = []
        while possible_moves:
            # Find the rightmost set bit
            move_bit = possible_moves & -possible_moves
            move_pos = move_bit.bit_length() - 1
            
            # Convert bit position to row, col (1-based for OthelloAction)
            row, col = move_pos // 8 + 1, move_pos % 8 + 1
            moves.append(OthelloAction(row, col))
            
            # Remove this move from consideration
            possible_moves &= possible_moves - 1
            
        return moves

    def _generate_moves_bitboard(self, my_pieces, opp_pieces):
        """
        Generate all valid moves using ultra-fast bitboard operations.
        This is the core optimization - generates all moves in parallel.
        """
        # Find all empty squares adjacent to opponent pieces
        empty = self.empty_bitboard
        
        # Generate moves in all 8 directions simultaneously
        moves = 0
        
        # North
        moves |= self._get_moves_direction(my_pieces, opp_pieces, empty, -8, 0xFFFFFFFFFFFFFFFF)
        
        # South  
        moves |= self._get_moves_direction(my_pieces, opp_pieces, empty, 8, 0xFFFFFFFFFFFFFFFF)
        
        # East
        moves |= self._get_moves_direction(my_pieces, opp_pieces, empty, 1, self.NOT_A_FILE)
        
        # West
        moves |= self._get_moves_direction(my_pieces, opp_pieces, empty, -1, self.NOT_H_FILE)
        
        # Northeast
        moves |= self._get_moves_direction(my_pieces, opp_pieces, empty, -7, self.NOT_A_FILE)
        
        # Northwest
        moves |= self._get_moves_direction(my_pieces, opp_pieces, empty, -9, self.NOT_H_FILE)
        
        # Southeast
        moves |= self._get_moves_direction(my_pieces, opp_pieces, empty, 9, self.NOT_A_FILE)
        
        # Southwest
        moves |= self._get_moves_direction(my_pieces, opp_pieces, empty, 7, self.NOT_H_FILE)
        
        return moves

    def _get_moves_direction(self, my_pieces, opp_pieces, empty, shift, mask):
        """
        Get valid moves in a specific direction using bitboard shifts.
        This is the core bitboard magic that makes move generation O(1).
        """
        # Shift my pieces in the direction and mask to prevent wrapping
        if shift > 0:
            adjacent_to_mine = (my_pieces << shift) & mask
        else:
            adjacent_to_mine = (my_pieces >> (-shift)) & mask
        
        # Find opponent pieces adjacent to my pieces
        adjacent_opponents = adjacent_to_mine & opp_pieces
        
        # Walk through opponent pieces to find valid moves
        moves = 0
        temp_opponents = adjacent_opponents
        
        # For each run of opponent pieces, find the end square
        while temp_opponents:
            # Shift opponents in the same direction to find continuation
            if shift > 0:
                next_opponents = (temp_opponents << shift) & mask & opp_pieces
            else:
                next_opponents = (temp_opponents >> (-shift)) & mask & opp_pieces
            
            # Find end squares (empty squares at the end of opponent runs)
            if shift > 0:
                end_squares = (temp_opponents << shift) & mask & empty
            else:
                end_squares = (temp_opponents >> (-shift)) & mask & empty
            
            moves |= end_squares
            temp_opponents = next_opponents
        
        return moves

    def make_move(self, action: OthelloAction) -> tuple[OptimizedBitboardPosition, int]:
        """
        Ultra-fast move making using parallel bitboard flipping.
        This is the core optimization for achieving deep search.
        """
        # Create new position (minimal copying)
        new_pos = OptimizedBitboardPosition()
        new_pos.BOARD_SIZE = self.BOARD_SIZE
        new_pos.maxPlayer = not self.maxPlayer  # Switch player
        new_pos.white_bitboard = self.white_bitboard
        new_pos.black_bitboard = self.black_bitboard
        new_pos.empty_bitboard = self.empty_bitboard
        new_pos.NOT_A_FILE = self.NOT_A_FILE
        new_pos.NOT_H_FILE = self.NOT_H_FILE
        new_pos.NOT_AB_FILE = self.NOT_AB_FILE
        new_pos.NOT_GH_FILE = self.NOT_GH_FILE

        # Handle pass move
        if action.is_pass_move:
            return new_pos, 0

        # Convert to bit position
        row, col = action.row - 1, action.col - 1
        bit_pos = row * 8 + col
        move_mask = 1 << bit_pos
        
        # Validate move is on empty square
        if not (new_pos.empty_bitboard & move_mask):
            raise ValueError("IllegalMoveException")
        
        # Get player bitboards
        if self.maxPlayer:
            my_pieces = new_pos.white_bitboard
            opp_pieces = new_pos.black_bitboard
        else:
            my_pieces = new_pos.black_bitboard
            opp_pieces = new_pos.white_bitboard
        
        # Place the piece
        if self.maxPlayer:
            new_pos.white_bitboard |= move_mask
        else:
            new_pos.black_bitboard |= move_mask
        new_pos.empty_bitboard &= ~move_mask
        
        # Perform flipping in all directions using parallel bitboard operations
        total_flipped = 0
        flips = 0
        
        # All 8 directions with their shift amounts and masks
        directions = [
            (-8, 0xFFFFFFFFFFFFFFFF),  # North
            (8, 0xFFFFFFFFFFFFFFFF),   # South
            (1, self.NOT_A_FILE),      # East
            (-1, self.NOT_H_FILE),     # West
            (-7, self.NOT_A_FILE),     # Northeast
            (-9, self.NOT_H_FILE),     # Northwest
            (9, self.NOT_A_FILE),      # Southeast
            (7, self.NOT_H_FILE),      # Southwest
        ]
        
        for shift, mask in directions:
            flips |= self._get_flips_direction(bit_pos, shift, mask, my_pieces, opp_pieces)
        
        # Apply all flips at once
        if flips:
            total_flipped = bin(flips).count('1')
            if self.maxPlayer:
                new_pos.white_bitboard |= flips
                new_pos.black_bitboard &= ~flips
            else:
                new_pos.black_bitboard |= flips
                new_pos.white_bitboard &= ~flips
        
        return new_pos, total_flipped

    def _get_flips_direction(self, bit_pos, shift, mask, my_pieces, opp_pieces):
        """
        Get all pieces to flip in a specific direction using bitboard operations.
        This replaces the slow loop-based flipping with parallel bitboard operations.
        """
        flips = 0
        
        # Start from the placed piece and walk in the direction
        if shift > 0:
            current = (1 << bit_pos) << shift
        else:
            current = (1 << bit_pos) >> (-shift)
        
        current &= mask  # Apply edge mask
        
        # Collect opponent pieces in this direction
        opponent_run = 0
        
        # Walk through opponent pieces
        while current and (current & opp_pieces):
            opponent_run |= current
            if shift > 0:
                current = (current << shift) & mask
            else:
                current = (current >> (-shift)) & mask
        
        # If we ended on our own piece, flip the opponent run
        if current and (current & my_pieces):
            flips = opponent_run
        
        return flips

    def clone(self):
        """Ultra-fast cloning with minimal object creation."""
        new_pos = OptimizedBitboardPosition()
        new_pos.BOARD_SIZE = self.BOARD_SIZE
        new_pos.maxPlayer = self.maxPlayer
        new_pos.white_bitboard = self.white_bitboard
        new_pos.black_bitboard = self.black_bitboard
        new_pos.empty_bitboard = self.empty_bitboard
        new_pos.NOT_A_FILE = self.NOT_A_FILE
        new_pos.NOT_H_FILE = self.NOT_H_FILE
        new_pos.NOT_AB_FILE = self.NOT_AB_FILE
        new_pos.NOT_GH_FILE = self.NOT_GH_FILE
        return new_pos

    def to_move(self):
        """Check which player's turn it is"""
        return self.maxPlayer

    def print_board(self):
        """Print the current board for debugging"""
        print("  ", end="")
        for c in range(8):
            print(f"{c+1:2}", end="")
        print()
        
        for r in range(8):
            print(f"{r+1:2}", end="")
            for c in range(8):
                bit_pos = r * 8 + c
                if self.white_bitboard & (1 << bit_pos):
                    print(" W", end="")
                elif self.black_bitboard & (1 << bit_pos):
                    print(" B", end="")
                else:
                    print(" .", end="")
            print()
        print(f"To move: {'White' if self.maxPlayer else 'Black'}")

    def to_string(self):
        """Convert bitboard position back to string format"""
        result = "W" if self.maxPlayer else "B"
        
        for r in range(8):
            for c in range(8):
                bit_pos = r * 8 + c
                if self.white_bitboard & (1 << bit_pos):
                    result += "O"
                elif self.black_bitboard & (1 << bit_pos):
                    result += "X"
                else:
                    result += "E"
                    
        return result
