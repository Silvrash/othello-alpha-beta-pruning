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
        # root = Node(othello_position, self.search_depth, None, evaluator=self.evaluator)
        # if root.best_move is None:
        #     return OthelloAction(0, 0, True)  # if no best moves passing
        # # print("\n\nBEST MOVE", root.best_move)
        # return root.best_move
        if othello_position.maxPlayer:
            return self.max_value(othello_position, float("-inf"), float("inf"), 1)
        else:
            return self.min_value(othello_position, float("-inf"), float("inf"), 1)

    def max_value(
        self, pos: OthelloPosition, alpha: float, beta: float, depth: int
    ) -> OthelloAction:
        self.__force_stop_if_time_elapsed()
        possible_moves = pos.get_moves()

        is_leaf = not possible_moves
        is_max_depth = depth == self.search_depth

        # If no legal moves or reached max depth, evaluate the node
        if is_leaf or is_max_depth:
            val = self.evaluator.evaluate(pos)
            leaf = OthelloAction(0, 0, True)
            leaf.value = val
            return leaf

        best_value = float("-inf")
        best_action = None

        for action in possible_moves:
            self.__force_stop_if_time_elapsed()
            child_pos = pos.make_move(action)
            child_eval_action = self.min_value(child_pos, alpha, beta, depth + 1)
            child_value = child_eval_action.value

            # choose the maximum
            if child_value > best_value:
                best_value = child_value
                best_action = action
                best_action.value = child_value

            # update alpha
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break  # beta cutoff

        return best_action

    def min_value(
        self, pos: OthelloPosition, alpha: float, beta: float, depth: int
    ) -> OthelloAction:
        self.__force_stop_if_time_elapsed()
        possible_moves = pos.get_moves()

        is_leaf = not possible_moves
        is_max_depth = depth == self.search_depth

        # If no legal moves(is_leaf) or reached max depth, evaluate the node
        if is_leaf or is_max_depth:
            val = self.evaluator.evaluate(pos)
            leaf = OthelloAction(0, 0, True)
            leaf.value = val
            return leaf

        best_value = float("inf")
        best_action = None

        for action in possible_moves:
            self.__force_stop_if_time_elapsed()
            child_pos = pos.make_move(action)
            child_eval_action = self.max_value(child_pos, alpha, beta, depth + 1)
            child_value = child_eval_action.value

            # choose the minimum
            if child_value < best_value:
                best_value = child_value
                best_action = action
                best_action.value = child_value

            # update beta
            beta = min(beta, best_value)
            if alpha >= beta:
                break  # alpha cutoff

        return best_action
