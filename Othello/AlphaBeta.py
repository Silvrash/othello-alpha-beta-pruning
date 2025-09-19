from ast import Set
import time
from typing import Callable, List
from Node import Node
from OthelloPosition import OthelloPosition
from OthelloAlgorithm import OthelloAlgorithm
from CountingEvaluator import CountingEvaluator
from OthelloAction import OthelloAction


class StopSignal(Exception):
    pass


class AlphaBeta(OthelloAlgorithm):
    """
    This is where you implement the alpha-beta algorithm.
        See OthelloAlgorithm for details

    Author:
    """

    DefaultDepth = 5

    def __init__(self, othello_evaluator=CountingEvaluator(), depth=DefaultDepth):
        self.evaluator = othello_evaluator
        self.search_depth = depth
        self.time_limit = None
        self.start_time = None
        self.look_up_table = {}

    def set_evaluator(self, othello_evaluator):
        self.evaluator = othello_evaluator

    def set_search_depth(self, depth):
        self.search_depth = depth

    def set_time_limit(self, time_limit):
        self.start_time = time.time()
        self.time_limit = time_limit

    def __force_stop_if_time_elapsed(self):
        if (
            self.start_time
            and self.time_limit
            and (time.time() - self.start_time) >= self.time_limit
        ):
            raise StopSignal()

    def evaluate(self, othello_position: OthelloPosition) -> OthelloAction:
        root = Node(othello_position, self.search_depth, None)
        if root.best_move is None:
            return OthelloAction(0, 0, True)  # if no best moves passing
        # print("\n\nBEST MOVE", root.best_move)
        return root.best_move

    def max_value(
        self, pos: OthelloPosition, alpha: float, beta: float, depth: int
    ) -> OthelloAction:
        self.__force_stop_if_time_elapsed()
        possible_moves = pos.get_moves()

        # If leaf (no moves or reached depth) return a "value-only" action
        if self.__is_leaf(possible_moves) or depth >= self.search_depth:
            val = self.evaluator.evaluate(pos)
            leaf = OthelloAction(0, 0, True)
            leaf.value = val
            return leaf

        best_value = float("-inf")
        best_action = None

        for action in possible_moves:
            child_pos = pos.clone().make_move(action)
            child_eval_action = self.min_value(child_pos, alpha, beta, depth + 1)
            child_value = child_eval_action.value

            # choose the maximum
            if child_value > best_value:
                best_value = child_value
                # create a fresh action to return (avoid mutating original action objects)
                best_action = OthelloAction(action.row, action.col, action.is_pass_move)
                best_action.value = child_value

            # update alpha
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break  # beta cutoff

        # If no legal moves found (defensive), return pass
        if best_action is None:
            pass_action = OthelloAction(0, 0, True)
            pass_action.value = self.evaluator.evaluate(pos)
            return pass_action

        return best_action

    def min_value(
        self, pos: OthelloPosition, alpha: float, beta: float, depth: int
    ) -> OthelloAction:
        self.__force_stop_if_time_elapsed()
        possible_moves = pos.get_moves()

        if self.__is_leaf(possible_moves) or depth >= self.search_depth:
            val = self.evaluator.evaluate(pos)
            leaf = OthelloAction(0, 0, True)
            leaf.value = val
            return leaf

        best_value = float("inf")
        best_action = None

        for action in possible_moves:
            child_pos = pos.clone().make_move(action)
            child_eval_action = self.max_value(child_pos, alpha, beta, depth + 1)
            child_value = child_eval_action.value

            # choose the minimum
            if child_value < best_value:
                best_value = child_value
                best_action = OthelloAction(action.row, action.col, action.is_pass_move)
                best_action.value = child_value

            # update beta
            beta = min(beta, best_value)
            if alpha >= beta:
                break  # alpha cutoff

        if best_action is None:
            pass_action = OthelloAction(0, 0, True)
            pass_action.value = self.evaluator.evaluate(pos)
            return pass_action

        return best_action

    def __is_leaf(self, moves: list[OthelloAction]):
        return not moves
