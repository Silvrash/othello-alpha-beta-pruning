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
                "BEEEEEEEEEEEEEEEEEEEEOEEEEEEOOEEEEEEXOEEEEEEEEEEEEEEEEEEEEEEEEEEE"
            )
            time_limit = 1

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
        # print(root.state.get_moves())
        try:
            move = algorithm.evaluate(pos)
            depth += 1

            if not best_move or move.value > best_move.value:
                best_move = move

        except StopSignal:
            # time expired
            break


    if not best_move:
        best_move = OthelloAction(0, 0, True)

    # Send the chosen move to stdout (print it)
    best_move.print_move()
    # print(best_move.value)
    # print(pos.get_moves())
    # pos.print_board()
    end = time.time()
    # print(end - start, f'max-depth reached: {depth}') # Only for debugging, print nothing but the move in the final version
