import time
import sys
from OthelloAction import OthelloAction
from OthelloPosition import OthelloPosition
from AlphaBeta import AlphaBeta, StopSignal
from CountingEvaluator import CountingEvaluator

import math
import time
from typing import Callable


def alpha_beta(
    node: OthelloPosition,
    depth,
    alpha,
    beta,
    maximizing,
    evaluator: Callable[[OthelloPosition], int],
    stop_signal,
) -> int:
    moves = node.get_moves()

    # Terminal or depth cutoff
    if depth == 0 or (not moves and not has_any_moves_other_player(node)):
        return evaluator(node)

    if not moves:  # pass turn
        new_pos = node.make_move(OthelloAction(0, 0, True))
        return alpha_beta(
            new_pos, depth, alpha, beta, not maximizing, evaluator, stop_signal
        )

    if maximizing:
        value = -math.inf
        for move in moves:
            child = node.make_move(move)
            val = alpha_beta(
                child, depth - 1, alpha, beta, False, evaluator, stop_signal
            )
            value = max(value, val)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value

    else:
        value = math.inf
        for move in moves:
            child = node.make_move(move)
            val = alpha_beta(
                child, depth - 1, alpha, beta, True, evaluator, stop_signal
            )
            value = min(value, val)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value


def iterative_deepening(
    root: OthelloPosition, evaluator: Callable[[OthelloPosition], int], max_time
) -> tuple[OthelloAction, int]:
    start = time.time()
    best_move = None
    best_value = -math.inf

    depth = 1
    while True:
        if time.time() - start > max_time:
            break  # stop search, return last completed depth result

        moves = root.get_moves()
        if not moves:
            if not has_any_moves_other_player(root):
                return None, None  # game over
            else:
                return None, None  # must handle pass outside if needed

        current_best = None
        current_best_val = -math.inf

        for move in moves:
            child = root.make_move(move)
            val = alpha_beta(
                child, depth - 1, -math.inf, math.inf, root.maxPlayer, evaluator, None
            )
            if val > current_best_val:
                current_best_val = val
                current_best = move

        # Update after finishing this depth
        best_move = current_best
        best_value = current_best_val

        depth += 1

    return best_move, best_value


def has_any_moves_other_player(position: OthelloPosition) -> bool:
    other = position.make_move(OthelloAction(0, 0, True))
    return len(other.get_moves()) > 0


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
    pos = OthelloPosition(posString)
    # pos.print_board() # Only for debugging. The test script has it's own print

    # TODO: implement Iterative Deepening Search

    current_depth = 1
    # Which evaluator (heuristics) should be used
    algorithm = AlphaBeta(CountingEvaluator())
    # algorithm.set_time_limit(time_limit)
    evaluator = CountingEvaluator()
    best_action, best_value = iterative_deepening(pos, evaluator.evaluate, time_limit)

    max_depth = len([v for v in posString if v == "E"])

    # while time.time() - start < time_limit * 0.9:
    #     # Set the depth that AlbphaBeta will search to.
    #     algorithm.set_search_depth(current_depth)

    #     # if current_depth >= max_depth:
    #     #     break

    #     try:
    #         # Evaluate the position
    #         move = algorithm.evaluate(pos)

    #         best_action = move

    #         current_depth += 1
    #     except StopSignal:
    #         pass

    if best_action is None:
        best_action = OthelloAction(0, 0, True)
    # Send the chosen move to stdout (print it)
    best_action.print_move()

    # pos.make_move(move).print_board()

    end = time.time()
    # print(end - start) # Only for debugging, print nothing but the move in the final version
