import time
import sys
from OthelloPosition import OthelloPosition
from AlphaBeta import AlphaBeta
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
        else:
            posString = (
                "BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE"
            )
    start = time.time()
    pos = OthelloPosition(posString)
    # pos.print_board() # Only for debugging. The test script has it's own print

    # TODO: implement Iterative Deepening Search

    # Which evaluator (heuristics) should be used
    algorithm = AlphaBeta(CountingEvaluator())
    # Set the depth that AlbphaBeta will search to.
    algorithm.set_search_depth(6)
    # Evaluate the position
    move = algorithm.evaluate(pos)
    # Send the chosen move to stdout (print it)
    move.print_move()

    end = time.time()
    # print(end - start) # Only for debugging, print nothing but the move in the final version
