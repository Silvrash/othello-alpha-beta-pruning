import time
import sys
from OthelloPosition import OthelloPosition
from AlphaBeta import AlphaBeta, StopSignal
from HeuristicEvaluator import HeuristicEvaluator


class Othello(object):
    """
    Example of a main class for Othello that starts the game.
    This version only searches to a fixed depth. You need to implement 
    Iterative Deepening Search using the time limit argument.
    
    Author: Ola Ringdahl

    Args:
        arg1: Position to evaluate (a string of length 65 representing the board).
        arg2: Time limit in seconds
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
        posString = (
            "BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE"
        )
        time_limit = 1
    start = time.time()
    pos = OthelloPosition(posString)
    # pos.print_board() # Only for debugging. The test script has it's own print

    algorithm = AlphaBeta(HeuristicEvaluator(pos.maxPlayer))
    move = None

    # Apply time buffer - be more aggressive with time usage
    time_limit = time_limit * 0.90

    # Iterative deepening: start from depth 1 and increment
    current_depth = 1
    depth_reached = 0

    while time.time() - start < time_limit:

        algorithm.set_search_depth(current_depth)
        elapsed_time = time.time() - start
        remaining_time = time_limit - elapsed_time

        # # Don't start a new depth if we don't have enough time
        # if remaining_time < 0.05:  # Need at least 0.05 seconds
        #     break

        # Evaluate the position
        algorithm.set_time_limit(remaining_time)

        try:
            # Search to current depth
            move = algorithm.evaluate(pos)
            depth_reached = current_depth
            current_depth += 1
        except StopSignal:
            # Time limit exceeded during current depth search
            break

    # Send the chosen move to stdout (print it)
    move.print_move()

    if not move.is_pass_move:
        print(f"Depth reached: {depth_reached}")

    end = time.time()
    # print(end - start) # Only for debugging, print nothing but the move in the final version
