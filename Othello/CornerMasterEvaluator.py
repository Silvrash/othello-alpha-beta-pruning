from OthelloAction import OthelloAction
from OthelloEvaluator import OthelloEvaluator
from BitboardOthelloPosition import BitboardOthelloPosition

class CornerMasterEvaluator(OthelloEvaluator):
    """
    Evaluator designed to dominate corner control and edge maximization.
    
    Strategy:
    1. NEVER give up corners - massive penalty for allowing opponent corners
    2. Once we have a corner, aggressively maximize the connected edge
    3. Heavily penalize X-squares and C-squares that risk corner loss
    4. Use piece counting as tiebreaker, but corners dominate everything
    """
    
    def __init__(self):
        # Corner positions - most critical
        self.corner_mask = (1 << 0) | (1 << 7) | (1 << 56) | (1 << 63)
        self.corners = [(0, 0), (0, 7), (7, 0), (7, 7)]
        
        # X-squares - extremely dangerous (diagonal to corners)
        self.x_square_mask = (1 << 9) | (1 << 14) | (1 << 49) | (1 << 54)
        self.x_squares = [(1, 1), (1, 6), (6, 1), (6, 6)]
        
        # C-squares - dangerous (adjacent to corners)
        self.c_square_mask = (1 << 1) | (1 << 8) | (1 << 48) | (1 << 57) | (1 << 62) | (1 << 6) | (1 << 15)
        self.c_squares = [(0, 1), (1, 0), (6, 0), (7, 1), (7, 6), (0, 6), (1, 7)]
        
        # Edge positions connected to each corner
        self.corner_edges = {
            (0, 0): [(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0)],  # Top-left
            (0, 7): [(0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (0, 1), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)],  # Top-right
            (7, 0): [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (6, 0), (5, 0), (4, 0), (3, 0), (2, 0), (1, 0)],  # Bottom-left
            (7, 7): [(7, 6), (7, 5), (7, 4), (7, 3), (7, 2), (7, 1), (6, 7), (5, 7), (4, 7), (3, 7), (2, 7), (1, 7)]   # Bottom-right
        }
        
        # All edge positions
        self.edge_mask = (
            # Top and bottom edges
            (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6) |
            (1 << 57) | (1 << 58) | (1 << 59) | (1 << 60) | (1 << 61) | (1 << 62) |
            # Left and right edges
            (1 << 8) | (1 << 16) | (1 << 24) | (1 << 32) | (1 << 40) | (1 << 48) |
            (1 << 15) | (1 << 23) | (1 << 31) | (1 << 39) | (1 << 47) | (1 << 55)
        )
        
        # Bitboard edge masks for preventing wraparound in bit operations
        self.NOT_A_FILE = 0xFEFEFEFEFEFEFEFE  # Mask excludes A-file (leftmost column)
        self.NOT_H_FILE = 0x7F7F7F7F7F7F7F7F  # Mask excludes H-file (rightmost column)
    
    def evaluate(self, othello_position: BitboardOthelloPosition, action) -> float:
        """
        Advanced evaluation with dynamic game phase detection based on corner control.
        
        Game Phase Strategy:
        1. EARLY GAME: No corners captured - Focus on mobility and avoiding danger squares
        2. MID GAME: At least one corner captured - Balance corners, edges, and stability  
        3. LATE GAME: High piece density - Focus on piece count and corner consolidation
        
        The key insight is that corner capture fundamentally changes the game dynamics,
        not just the piece count threshold.
        """
        
        # Get bitboards for current player and opponent
        if othello_position.maxPlayer:
            my_bitboard = othello_position.white_bitboard
            opp_bitboard = othello_position.black_bitboard
        else:
            my_bitboard = othello_position.black_bitboard
            opp_bitboard = othello_position.white_bitboard
        
        # Count pieces for traditional game phase detection
        my_pieces = bin(my_bitboard).count('1')
        opp_pieces = bin(opp_bitboard).count('1')
        total_pieces = my_pieces + opp_pieces
        
        # 1. CORNER ANALYSIS - Foundation of our strategy
        my_corners = bin(my_bitboard & self.corner_mask).count('1')
        opp_corners = bin(opp_bitboard & self.corner_mask).count('1')
        total_corners = my_corners + opp_corners
        corner_diff = my_corners - opp_corners
        
        # 2. MOBILITY CALCULATION - Critical strategic factor
        # "One should maximize the number of moves one has, and minimize the number
        # of moves available to one's opponent" - Classic Othello principle
        my_mobility = len(othello_position.get_moves())
        
        # Efficient opponent mobility calculation
        temp_pos = othello_position.clone()
        temp_pos.maxPlayer = not othello_position.maxPlayer
        opp_mobility = len(temp_pos.get_moves())
        mobility_diff = my_mobility - opp_mobility
        
        # 3. FRONTIER/FRINGE ANALYSIS - Mobility indicator
        # "Frontier" discs are next to empty squares - each move must be adjacent to opponent disc
        my_frontier = self._count_frontier_discs(my_bitboard, othello_position.empty_bitboard)
        opp_frontier = self._count_frontier_discs(opp_bitboard, othello_position.empty_bitboard)
        frontier_diff = opp_frontier - my_frontier  # Lower frontier is better (fewer weak points)
        
        # 4. PARITY ANALYSIS - "Last to flip" advantage
        # "As the last player to put down a disc flips last, one should favor situations 
        # in which one is the last to flip"
        parity_bonus = self._calculate_parity_advantage(total_pieces, my_pieces, opp_pieces)
        
        # 5. DYNAMIC GAME PHASE DETECTION
        if total_corners == 0:
            # EARLY GAME PHASE: No corners captured yet
            return self._evaluate_early_game(my_bitboard, opp_bitboard, mobility_diff, 
                                           frontier_diff, parity_bonus, my_pieces, opp_pieces, total_pieces)
        elif total_pieces < 45:  # Switch to greedy mode earlier
            # MID GAME PHASE: Corner(s) captured, but board not full
            return self._evaluate_mid_game(my_bitboard, opp_bitboard, corner_diff, 
                                         mobility_diff, frontier_diff, parity_bonus,
                                         my_pieces, opp_pieces, total_pieces)
        else:
            # LATE GAME PHASE: High piece density, GREEDY APPROACH
            # Switch to greedy mode when board is ~70% full (45/64 pieces)
            return self._evaluate_late_game(my_bitboard, opp_bitboard, corner_diff,
                                          mobility_diff, parity_bonus, my_pieces, opp_pieces)
        
    def _evaluate_early_game(self, my_bitboard, opp_bitboard, mobility_diff, 
                            frontier_diff, parity_bonus, my_pieces, opp_pieces, total_pieces):
        """
        Early game evaluation: Focus on mobility and avoiding danger squares.
        
        Strategy: Maximize mobility while avoiding X-squares and C-squares that
        could give the opponent corner access. This phase continues until ANY
        player captures a corner, which fundamentally changes the game dynamics.
        """
        score = 0
        
        # 1. MOBILITY DOMINANCE - Primary factor in early game
        # "Maximize the number of moves one has, minimize opponent's moves"
        score += mobility_diff * 120  # Very high weight for mobility
        
        # 1a. FRONTIER CONTROL - Minimize vulnerable pieces
        # Fewer frontier discs means fewer attack vectors for opponent
        score += frontier_diff * 15  # Bonus for having fewer frontier discs
        
        # 2. X-SQUARE AVOIDANCE - Extremely dangerous in early game
        my_x_squares = bin(my_bitboard & self.x_square_mask).count('1')
        opp_x_squares = bin(opp_bitboard & self.x_square_mask).count('1')
        x_square_penalty = (my_x_squares - opp_x_squares) * 800  # Massive penalty
        score -= x_square_penalty
        
        # 3. C-SQUARE AVOIDANCE - Risky in early game
        my_c_squares = bin(my_bitboard & self.c_square_mask).count('1')
        opp_c_squares = bin(opp_bitboard & self.c_square_mask).count('1')
        c_square_penalty = (my_c_squares - opp_c_squares) * 400  # High penalty
        score -= c_square_penalty
        
        # 4. EDGE CONTROL - Moderate bonus for stable positions
        my_edges = bin(my_bitboard & self.edge_mask).count('1')
        opp_edges = bin(opp_bitboard & self.edge_mask).count('1')
        edge_bonus = (my_edges - opp_edges) * 20
        score += edge_bonus
        
        # 5. PIECE COUNT - Minor factor in early game
        piece_diff = my_pieces - opp_pieces
        score += piece_diff * 2  # Low weight - don't focus on pieces yet
        
        # 6. PARITY ADVANTAGE - Early positioning for endgame
        score += parity_bonus * 10  # Moderate weight in early game
        
        # 7. TEMPO BONUS - Reward having more pieces early for initiative
        if total_pieces < 16:  # Very early game
            score += piece_diff * 5  # Slightly higher weight for early tempo
        
        return score
    
    def _evaluate_mid_game(self, my_bitboard, opp_bitboard, corner_diff, mobility_diff,
                          frontier_diff, parity_bonus, my_pieces, opp_pieces, total_pieces):
        """
        Mid game evaluation: Balance corners, edges, mobility, and stability.
        
        Strategy: Once corners are in play, shift focus to consolidating corner
        advantages while maintaining mobility. This is the most complex phase
        requiring balance between multiple factors.
        """
        score = 0
        
        # 1. CORNER SUPREMACY - Now the dominant factor
        score += corner_diff * 3000  # Massive corner bonus
        
        # 2. EDGE MAXIMIZATION - Critical for corner consolidation
        edge_bonus = 0
        for corner_pos in self.corners:
            corner_bit = corner_pos[0] * 8 + corner_pos[1]
            
            # If we control this corner, get bonus for connected edges
            if my_bitboard & (1 << corner_bit):
                connected_edges = self.corner_edges[corner_pos]
                for edge_pos in connected_edges:
                    edge_bit = edge_pos[0] * 8 + edge_pos[1]
                    if my_bitboard & (1 << edge_bit):
                        edge_bonus += 100  # Big bonus for corner-connected edges
            
            # If opponent controls this corner, penalty for their connected edges
            elif opp_bitboard & (1 << corner_bit):
                connected_edges = self.corner_edges[corner_pos]
                for edge_pos in connected_edges:
                    edge_bit = edge_pos[0] * 8 + edge_pos[1]
                    if opp_bitboard & (1 << edge_bit):
                        edge_bonus -= 100  # Penalty for opponent's corner edges
        
        score += edge_bonus
        
        # 3. MOBILITY - Still important but secondary to corners
        score += mobility_diff * 60  # Reduced from early game but still significant
        
        # 3a. FRONTIER CONTROL - Stability through fewer weak points
        score += frontier_diff * 20  # Higher weight as stability becomes important
        
        # 4. SMART X-SQUARE EVALUATION - Context-dependent
        safe_x_penalty = 0
        unsafe_x_penalty = 0
        
        for i, x_pos in enumerate(self.x_squares):
            x_bit = x_pos[0] * 8 + x_pos[1]
            corner_pos = self.corners[i]  # Corresponding corner
            corner_bit = corner_pos[0] * 8 + corner_pos[1]
            
            if my_bitboard & (1 << x_bit):
                if my_bitboard & (1 << corner_bit):
                    safe_x_penalty += 0  # X-square is safe, no penalty
                else:
                    unsafe_x_penalty += 600  # Still dangerous without corner
        
        score -= unsafe_x_penalty
        
        # 5. C-SQUARE EVALUATION - Less critical once corners are captured
        my_c_squares = bin(my_bitboard & self.c_square_mask).count('1')
        c_square_penalty = my_c_squares * 200  # Reduced penalty in mid-game
        score -= c_square_penalty
        
        # 6. PARITY POSITIONING - Critical for endgame preparation  
        score += parity_bonus * 25  # Higher weight as endgame approaches
        
        # 7. PIECE COUNT - Growing importance
        piece_diff = my_pieces - opp_pieces
        score += piece_diff * 10  # Moderate weight
        
        return score
    
    def _evaluate_late_game(self, my_bitboard, opp_bitboard, corner_diff,
                           mobility_diff, parity_bonus, my_pieces, opp_pieces):
        """
        Late game evaluation: GREEDY APPROACH - Maximize piece count above all else.
        
        Strategy: With the board nearly full, the game is about who has more pieces.
        Use a greedy approach focused on maximizing our piece count while maintaining
        any structural advantages we have.
        
        "In the endgame, every piece counts - be greedy!"
        """
        score = 0
        
        # 1. PIECE COUNT - DOMINANT factor in late game (GREEDY APPROACH)
        piece_diff = my_pieces - opp_pieces
        score += piece_diff * 200  # Massive weight for pieces - this is what wins games!
        
        # 2. PARITY DOMINANCE - "Favor being the last to flip"
        # Critical in endgame as it often determines who gets the final pieces
        score += parity_bonus * 100  # Maximum weight in endgame
        
        # 3. MOBILITY - Essential for accessing remaining squares
        # In late game, mobility often directly translates to more pieces
        if mobility_diff != 0:
            score += mobility_diff * 80  # High weight - more moves = more pieces
        
        # 4. CORNER CONSOLIDATION - Only if it leads to more pieces
        # Corners are still valuable but secondary to piece count
        score += corner_diff * 500  # Reduced from earlier phases
        
        # 5. STABILITY - Stable pieces can't be lost
        # Important for protecting our piece advantage
        my_stable = self._count_stable_discs_simple(my_bitboard, opp_bitboard)
        opp_stable = self._count_stable_discs_simple(opp_bitboard, my_bitboard)
        stability_diff = my_stable - opp_stable
        score += stability_diff * 60  # High weight for keeping pieces safe
        
        # 6. EDGE COMPLETION - Only for stability, not strategy
        # Complete edges to secure pieces, but don't overvalue
        edge_bonus = 0
        for corner_pos in self.corners:
            corner_bit = corner_pos[0] * 8 + corner_pos[1]
            
            if my_bitboard & (1 << corner_bit):
                connected_edges = self.corner_edges[corner_pos]
                edge_count = 0
                for edge_pos in connected_edges:
                    edge_bit = edge_pos[0] * 8 + edge_pos[1]
                    if my_bitboard & (1 << edge_bit):
                        edge_count += 1
                
                # Modest bonus for edge completion
                edge_bonus += edge_count * 10  # Reduced weight - focus on pieces
        
        score += edge_bonus
        
        # 7. GREEDY PIECE MAXIMIZATION BONUS
        # Extra reward for being significantly ahead in pieces
        if piece_diff > 5:
            score += piece_diff * 50  # Compound the advantage
        elif piece_diff < -5:
            score -= abs(piece_diff) * 30  # Penalty for being far behind
        
        return score
    
    def _count_stable_discs_simple(self, my_pieces, opp_pieces):
        """
        Simplified stable disc counting for late game evaluation.
        
        A disc is considered stable if it's a corner or connected to a corner
        along an edge. This is a fast approximation of true stability.
        """
        stable_count = 0
        
        # Count corners as stable
        stable_count += bin(my_pieces & self.corner_mask).count('1')
        
        # Count edge pieces connected to our corners as stable
        for corner_pos in self.corners:
            corner_bit = corner_pos[0] * 8 + corner_pos[1]
            
            if my_pieces & (1 << corner_bit):
                # This corner is ours, count connected edge pieces
                connected_edges = self.corner_edges[corner_pos]
                for edge_pos in connected_edges:
                    edge_bit = edge_pos[0] * 8 + edge_pos[1]
                    if my_pieces & (1 << edge_bit):
                        stable_count += 1
        
        return stable_count
    
    def _count_frontier_discs(self, my_pieces, empty_bitboard):
        """
        Count "frontier" or "fringe" discs - pieces adjacent to empty squares.
        
        These are vulnerable pieces that give the opponent potential move options.
        Lower frontier count is generally better as it means fewer weak points.
        
        Simplified algorithm: A piece is a frontier disc if any adjacent square is empty.
        """
        frontier_pieces = 0
        
        # For each direction, find pieces that have empty squares adjacent
        # North
        frontier_pieces |= my_pieces & (empty_bitboard << 8)
        # South  
        frontier_pieces |= my_pieces & (empty_bitboard >> 8)
        # East (with A-file mask to prevent wraparound)
        frontier_pieces |= my_pieces & ((empty_bitboard & self.NOT_A_FILE) >> 1)
        # West (with H-file mask to prevent wraparound)
        frontier_pieces |= my_pieces & ((empty_bitboard & self.NOT_H_FILE) << 1)
        # Northeast
        frontier_pieces |= my_pieces & ((empty_bitboard & self.NOT_A_FILE) << 7)
        # Northwest  
        frontier_pieces |= my_pieces & ((empty_bitboard & self.NOT_H_FILE) << 9)
        # Southeast
        frontier_pieces |= my_pieces & ((empty_bitboard & self.NOT_A_FILE) >> 9)
        # Southwest
        frontier_pieces |= my_pieces & ((empty_bitboard & self.NOT_H_FILE) >> 7)
        
        return bin(frontier_pieces).count('1')
    
    def _calculate_parity_advantage(self, total_pieces, my_pieces, opp_pieces):
        """
        Calculate parity advantage - the benefit of being the last to move.
        
        "As the last player to put down a disc flips last, one should favor 
        situations in which one is the last to flip."
        
        Parity considerations:
        1. Overall game parity (who moves last in the game)
        2. Region parity (who fills the last square in closed regions)
        3. Tempo advantage (having the initiative)
        """
        parity_score = 0
        
        # 1. OVERALL GAME PARITY
        # With 64 squares total, if we're ahead in piece count on even total pieces,
        # we're more likely to move last
        remaining_squares = 64 - total_pieces
        
        if remaining_squares % 2 == 0:
            # Even number of moves remaining
            if my_pieces >= opp_pieces:
                parity_score += 5  # Slight advantage for being ahead
        else:
            # Odd number of moves remaining
            if my_pieces <= opp_pieces:
                parity_score += 5  # Slight advantage for being behind
        
        # 2. TEMPO CONSIDERATIONS
        # Being slightly behind in pieces can be advantageous in the middle game
        # as it often means having more move options
        piece_diff = my_pieces - opp_pieces
        
        if total_pieces < 40:  # Mid-game tempo
            if -2 <= piece_diff <= 0:  # Slightly behind or even
                parity_score += 3  # Tempo advantage
        elif total_pieces >= 50:  # Endgame positioning
            if piece_diff > 0:  # Ahead in pieces
                parity_score += piece_diff  # Direct advantage
        
        return parity_score
    
    def move_priority(self, action: OthelloAction) -> float:
        """
        Move ordering that prioritizes corner control above all else.
        """
        if action.is_pass_move:
            return float("-inf")
        
        # Convert to 0-based coordinates
        row_idx = action.row - 1
        col_idx = action.col - 1
        bit_pos = row_idx * 8 + col_idx
        
        # Corner moves get absolute highest priority
        if self.corner_mask & (1 << bit_pos):
            return 10000
        
        # Edge moves get high priority (especially if we have adjacent corner)
        elif self.edge_mask & (1 << bit_pos):
            return 1000
        
        # X-square moves get absolute lowest priority - NEVER take these early
        elif self.x_square_mask & (1 << bit_pos):
            return -10000
        
        # C-square moves get very low priority
        elif self.c_square_mask & (1 << bit_pos):
            return -5000
        
        # Everything else is neutral
        else:
            return 0
