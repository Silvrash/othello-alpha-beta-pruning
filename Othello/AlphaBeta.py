import time
from OthelloPosition import OthelloPosition
from OthelloNode import OthelloNode
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

        # store nodes already traversed
        self.look_up_table = {}

    def set_evaluator(
        self,
        othello_evaluator,
    ):
        self.evaluator = othello_evaluator  # change to your own evaluator

    def set_search_depth(self, depth):
        self.search_depth = depth  # use iterative deepening search to decide depth

    def set_time_limit(self, time_limit):
        self.start_time = time.time()
        self.time_limit = time_limit

    def __force_stop_if_time_elapsed(self):
        if (
            self.start_time
            and self.time_limit
            and time.time() - self.start_time >= self.time_limit
        ):
            raise StopSignal
        else:
            pass

    def evaluate(self, othello_position: OthelloPosition) -> OthelloAction:
        # TODO: implement the alpha-beta algorithm
        alpha = float("-inf")
        beta = float("inf")
        # print('\n starting')
        return self.max_value(othello_position, alpha, beta, 0)

    def max_value(
        self, pos: OthelloPosition, alpha: float, beta: float, depth: int
    ) -> OthelloAction:
        # print('computing max')
        self.__force_stop_if_time_elapsed()
        possible_moves = pos.get_moves()
        final_action = OthelloAction(0, 0, True)

        # print(f"max possible {possible_moves}")

        if self.__is_leaf(possible_moves) or depth >= self.search_depth:
            value = self.evaluator.evaluate(pos)
            final_action.value = value
            return final_action

        value = float("-inf")
        final_action.value = value

        for action in possible_moves:
            action_pos = pos.clone().make_move(action)

            val = self.min_value(action_pos, alpha, beta, depth + 1)

            if val.value > final_action.value:
                action.value += val.value
                final_action = action

            alpha = max(alpha, final_action.value)

            if alpha >= beta:
                # cut off
                break

        return final_action

    def min_value(self, pos: OthelloPosition, alpha: float, beta: float, depth: int) -> OthelloAction:
        # print("computing min")
        self.__force_stop_if_time_elapsed()
        possible_moves = pos.get_moves()
        value = float("inf")
        final_action = OthelloAction(0, 0, True)

        if self.__is_leaf(possible_moves) or depth >= self.search_depth:
            value = self.evaluator.evaluate(pos)
            final_action.value = value
            return final_action

        
        for action in possible_moves:
            action_pos = pos.clone().make_move(action)

            val = self.max_value(action_pos, alpha, beta, depth + 1)

            if val.value < final_action.value:
                action.value += val.value
                final_action = action

            beta = min(beta, final_action.value)

            if alpha >= beta:
                # cut off
                break
        return final_action

    def __is_leaf(self, moves: list[OthelloAction]):
        return not moves
