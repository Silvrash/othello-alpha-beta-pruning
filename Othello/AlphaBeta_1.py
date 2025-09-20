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
        if(root.best_move is None): return OthelloAction(0,0,True) #if no best moves passing
        #print("\n\nBEST MOVE", root.best_move)
        return root.best_move