import time
import sys
from OthelloAction import OthelloAction
from OthelloPosition import OthelloPosition
from AlphaBeta_1 import AlphaBeta, StopSignal
from CountingEvaluator import CountingEvaluator

import math
import time
from typing import Callable

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
                "BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE"
            )
            time_limit = 1

    start = time.time()
    if posString[0] == "B":
        # Flip black and white pieces
        posString = "W" + posString[1:].replace("X", "t").replace("O", "X").replace("t", "O")

    pos = OthelloPosition(posString)
    # pos.print_board() # Only for debugging. The test script has it's own print

    # TODO: implement Iterative Deepening Search

    current_depth = 1
    # Which evaluator (heuristics) should be used
    algorithm = AlphaBeta(CountingEvaluator())
    algorithm.set_time_limit(time_limit * 0.9)

    max_depth = len([v for v in posString if v == "E"])

    while time.time() - start < time_limit * 0.9:
        # Set the depth that AlbphaBeta will search to.
        algorithm.set_search_depth(current_depth)

        # if current_depth >= max_depth:
        #     break

        try:
            # Evaluate the position
            move = algorithm.evaluate(pos)
            best_action = move

            current_depth += 1
        except StopSignal:
            pass

    if best_action is None:
        best_action = OthelloAction(0, 0, True)
    # Send the chosen move to stdout (print it)
    best_action.print_move()

    # pos.make_move(move).print_board()

    end = time.time()
    # print(end - start) # Only for debugging, print nothing but the move in the final version
