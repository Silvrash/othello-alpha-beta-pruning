import time
import sys
from OthelloAction import OthelloAction
from OthelloPosition import OthelloPosition
from AlphaBeta import AlphaBeta, StopSignal
from PrimaryEvaluator import PrimaryEvaluator

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

    pos = OthelloPosition(posString)
    
    # pos.print_board() # Only for debugging. The test script has it's own print

    # ITERATIVE DEEPENING SEARCH IMPLEMENTATION
    
    # Initialize search parameters
    current_depth = 1  # Start with depth 1
    algorithm = AlphaBeta(PrimaryEvaluator())  # Use advanced heuristic evaluator
    best_action = None  # Store the best move found
    
    # Apply 99% time buffer to account for evaluation overhead
    # This prevents timeout during move calculation
    time_limit = time_limit * 0.95

    # Iterative deepening loop
    while time.time() - start < time_limit:
        # Configure algorithm for current depth
        algorithm.set_search_depth(current_depth)
        
        # Calculate remaining time for this depth
        elapsed_time = time.time() - start
        remaining_time = time_limit - elapsed_time
        algorithm.set_time_limit(remaining_time)
        
        try:
            # Search to current depth
            move = algorithm.evaluate(pos)
            best_action = move  # Update best move if search completed
            
            # Increment depth for next iteration
            current_depth += 1
            
        except StopSignal:
            # Time limit exceeded during current depth search
            # Return best move from previous completed depth
            break

    # Handle case where no move was found (should not happen)
    if best_action is None:
        best_action = OthelloAction(0, 0, True)  # Pass move
        
    # Output the chosen move to stdout
    best_action.print_move()

    # pos.make_move(move).print_board()

    # end = time.time()
    # print(end - start) # Only for debugging, print nothing but the move in the final version

