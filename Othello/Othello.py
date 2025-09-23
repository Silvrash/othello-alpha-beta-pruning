import time
import sys
from BitboardOthelloPosition import BitboardOthelloPosition
from OptimizedBitboardPosition import OptimizedBitboardPosition
from SecondaryEvaluator import SecondaryEvaluator
from CountingEvaluator import CountingEvaluator
from OptimizedEvaluator import OptimizedEvaluator
from OthelloAction import OthelloAction
from OthelloPosition import OthelloPosition
from AlphaBeta import AlphaBeta, StopSignal
from PrimaryEvaluator import PrimaryEvaluator
from FastEvaluator import FastEvaluator
from BeatNaiveEvaluator import BeatNaiveEvaluator
from CornerMasterEvaluator import CornerMasterEvaluator
from GreedyEvaluator import GreedyEvaluator
import os

class Othello(object):
    """
    Main Othello game controller implementing iterative deepening search.
    
    This class orchestrates the game by implementing iterative deepening search
    with alpha-beta pruning. It progressively increases search depth within the
    given time limit to find the best possible move.
    
    The implementation uses a sophisticated heuristic evaluation system that
    considers multiple factors including corner control, stability, mobility,
    and positional advantages.
    
    Attributes:
        posString (str): 65-character string representing the game position
        time_limit (float): Maximum time allowed for move calculation
        algorithm (AlphaBeta): The alpha-beta pruning algorithm instance
        best_action (OthelloAction): The best move found by the algorithm
    
    Author: Afrasah Benjamin Arko & Sienichev Matvey
    Based on original framework by Ola Ringdahl
    """

    if __name__ == "__main__":
        """
        Main execution block for the Othello AI.
        
        Parses command line arguments for position string and time limit,
        then runs the iterative deepening search algorithm.
        
        Command line usage:
            python Othello.py [position_string] [time_limit]
            
        Args:
            position_string: 65-character string representing board state
            time_limit: Maximum search time in seconds
        """
        if len(sys.argv) > 1:
            try:
                posString = sys.argv[1]
            except ValueError:
                print("Error: Position must be a string")
                exit(1)
            except IndexError:
                print("Error: Position must be provided")
                exit(1)
            try:
                time_limit = float(sys.argv[2])
            except ValueError:
                print("Error: Time limit must be a number")
                exit(1)
            except IndexError:
                print("Error: Time limit must be provided")
                exit(1)
        else:
            # Default test position and time limit
            posString = (
                "BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE"
            )
            time_limit = 2

    start = time.time()

    pos = BitboardOthelloPosition(posString)
    
    # pos.print_board() # Only for debugging. The test script has it's own print
    # print('is white to move', pos.maxPlayer)
    # print('is black to move', not pos.maxPlayer)

    # ITERATIVE DEEPENING SEARCH IMPLEMENTATION
    # Increment depth from 1 up to maximum possible within time limit
    
    algorithm = AlphaBeta(GreedyEvaluator())
    best_action = None
    
    # Apply time buffer - be more aggressive with time usage
    time_limit = time_limit * 0.90
    
    # Iterative deepening: start from depth 1 and increment
    current_depth = 1
    
    while time.time() - start < time_limit:
        algorithm.set_search_depth(current_depth)
        elapsed_time = time.time() - start
        remaining_time = time_limit - elapsed_time
        
        # Don't start a new depth if we don't have enough time
        if remaining_time < 0.05:  # Need at least 0.05 seconds
            break
            
        algorithm.set_time_limit(remaining_time)
        
        try:
            # Search to current depth
            move = algorithm.evaluate(pos)

            best_action = move  # Update best move if search completed
                # print(f"Depth: {current_depth}, Move: {move}, Time: {elapsed_time}, score: {move.value}")
            # print(f"Depth: {current_depth}, Move: {move}")
            current_depth += 1
        except StopSignal:
            # Time limit exceeded during current depth search
            break

    # print(f"Best action: {best_action} {best_action.value}")
    # Handle case where no move was found
    if best_action is None:
        best_action = OthelloAction(0, 0, True)  # Pass move

    # os.makedirs(f"depth", exist_ok=True)
    # with open(f"depth/t{original_time_limit}s.txt", "a") as f:
    #     f.write(f"{current_depth} {move}\n")
    # Output the chosen move to stdout
    best_action.print_move()

    # pos.make_move(move).print_board()

    # end = time.time()
    # print(end - start) # Only for debugging, print nothing but the move in the final version

