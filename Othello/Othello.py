import time
import sys
from OthelloAction import OthelloAction
from OthelloNode import OthelloNode
from OthelloPosition import OthelloPosition
from AlphaBeta import AlphaBeta, StopSignal
from CountingEvaluator import CountingEvaluator


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

    if __name__ == "__main__":
        if len(sys.argv) > 1:
            posString = sys.argv[1]
            time_limit = float(sys.argv[2])
        else:
            posString = (
                # "BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE"
                "WEEEEEEEEEEOEEEEEEEEOOXEEEEEXXEEEEEEXOEEEEEEEEEEEEEEEEEEEEEEEEEEE"
                # (3,3)
            )
            time_limit = 5

    start = time.time()
    pos = OthelloPosition(posString)
    # pos.initialize()
    # pos.print_board() # Only for debugging. The test script has it's own print

    # TODO: implement Iterative Deepening Search

    best_move = None
    depth = 1
    # Which evaluator (heuristics) should be used
    algorithm = AlphaBeta(CountingEvaluator())
    algorithm.set_time_limit(time_limit)
    # print('time limit', time_limit)
    
    while True:
        # Set the depth that AlphaBeta will search to.
        algorithm.set_search_depth(depth)

        # Evaluate the position
        root = OthelloNode(pos)
        try:
            move = algorithm.evaluate(root)

            if not best_move or move.value > best_move.value:
                best_move = move
            
            depth += 1
            
        except StopSignal:
            # time expired
            break


    # Send the chosen move to stdout (print it)
    if best_move:
        best_move.print_move()

    end = time.time()
# (6, 4)
    root.state.make_move(best_move).print_board()
    # print(end - start, f'max-depth reached: {depth}') # Only for debugging, print nothing but the move in the final version
