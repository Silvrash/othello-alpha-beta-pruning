import time
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
        if self.start_time and self.time_limit and time.time() - self.start_time >= self.time_limit:
            raise StopSignal
        else:
            pass

    def evaluate(self, node: OthelloNode) -> OthelloAction:
        # TODO: implement the alpha-beta algorithm
        alpha = float("-inf")
        beta = float("inf")
        # print('\n starting')
        best_node = self.max_value(node, alpha, beta)
        return best_node.action

    def max_value(self, node: OthelloNode, alpha: float, beta: float) -> OthelloNode:
        # print('computing max')
        self.__force_stop_if_time_elapsed()
        possible_moves = node.state.get_moves()

        if self.__is_leaf(possible_moves) or node.depth >= self.search_depth:
            value = self.evaluator.evaluate(node.state)
            node.action.value = value
            return node

        node.action.value = float("-inf")
        max_node = node
        depth = node.depth + 1

        for action in possible_moves:
            # print(f"depth={node.depth}, player={'W' if node.state.maxPlayer else 'B'}, move=({action.row, action.col})")
            child_node = OthelloNode(node.state, depth, action, node)
            max_node = max(
                max_node,
                self.min_value(child_node, alpha, beta),
                key=lambda obj: obj.action.value,
            )
            alpha = max(alpha, node.action.value)

            if alpha >= beta:
                # cut off
                break

        return max_node

    def min_value(self, node: OthelloNode, alpha: float, beta: float) -> OthelloNode:
        # print("computing min")
        self.__force_stop_if_time_elapsed()
        possible_moves = node.state.get_moves()

        if self.__is_leaf(possible_moves) or node.depth >= self.search_depth:
            value = self.evaluator.evaluate(node.state)
            node.action.value = value
            return node

        node.action.value = float("inf")
        min_node = node
        depth = node.depth + 1

        for action in possible_moves:
            # print(
            #     f"depth={node.depth}, player={'W' if node.state.maxPlayer else 'B'}, move=({action.row, action.col})"
            # )
            child_node = OthelloNode(node.state, depth, action, node)
            # child_node.state.print_board()
            # action.print_move()
            min_node = min(
                min_node,
                self.max_value(child_node, alpha, beta),
                key=lambda obj: obj.action.value,
            )
            beta = min(beta, node.action.value)

            if alpha >= beta:
                # cut off
                break
        return min_node

    def __is_leaf(self, moves: list[OthelloAction]):
        return not moves
