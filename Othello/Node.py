from __future__ import annotations
from OthelloPosition import OthelloPosition
from OthelloAction import OthelloAction
from PrimaryEvaluator import PrimaryEvaluator
import sys


class Node:

    def __init__(
        self,
        pos: OthelloPosition,
        max_depth,
        parent=None,
        alpha=float("-inf"),
        beta=float("inf"),
        time_control=None,
        evaluator=PrimaryEvaluator(),
    ):
        self.position = pos
        self.parent = parent
        self.leaf = False
        self.alpha = alpha
        self.beta = beta
        self.compute_depth = max_depth
        self.best_move = None
        self.time_control = time_control
        self.evaluator = evaluator
        
        # Set recursion limit based on maximum branching factor
        # Othello max branching factor: 20 legal moves per turn
        # Max game length: 60 moves
        # Theoretical max recursive calls: 60 × 20 = 1,200
        if sys.getrecursionlimit() < 1200:
            sys.setrecursionlimit(1200)
        
        # if root
        if self.parent is None:
            self.depth = 0
            self.alpha_beta(self)
        else:
            self.depth = self.parent.depth + 1
            # if leaf
            if self.depth == max_depth:
                self.leaf = True

    def alpha_beta(self, node: Node):
        return self.max(node)

    def max(self, node: Node):
        node.time_control()
        best_move = None

        if node.leaf:
            node.time_control()
            return node.evaluator.evaluate(node.position)

        score = float("-inf")

        moves = node.position.get_moves()

        moves.sort(key=node.evaluator.move_priority, reverse=True)

        # pass if no legal moves
        if not moves:
            moves = [OthelloAction(0, 0, True)]

        for m in moves:
            node.time_control()
            new_position = node.position.make_move(m)
            child_node = Node(
                pos=new_position,
                max_depth=self.compute_depth,
                parent=node,
                alpha=node.alpha,
                beta=node.beta,
                time_control=node.time_control,
                evaluator=node.evaluator,
            )
            
            child_score = self.min(child_node)
            if score < child_score:
                score = child_score
                best_move = m

            node.best_move = best_move

            node.alpha = max(node.alpha, score)
            if node.alpha >= node.beta:
                break
            """ elif node.alpha < node.beta and self.position.maxPlayer == False:
                #print("oulelelel")
                break """
        return score

    def min(self, node: Node):
        node.time_control()
        best_move = None

        if node.leaf:
            node.time_control()
            return node.evaluator.evaluate(node.position)

        score = float("inf")

        moves = node.position.get_moves()

        moves.sort(key=node.evaluator.move_priority, reverse=True)

        # pass if no legal moves
        if not moves:
            moves = [OthelloAction(0, 0, True)]

        for m in moves:
            node.time_control()
            new_position = node.position.make_move(m)
            child_node = Node(
                pos=new_position,
                max_depth=self.compute_depth,
                parent=node,
                alpha=node.alpha,
                beta=node.beta,
                time_control=node.time_control,
                evaluator=node.evaluator,
            )
            

            child_score = self.max(child_node)
            if score > child_score:
                score = child_score
                best_move = m
            node.beta = min(node.beta, score)
            node.best_move = best_move
            if node.alpha >= node.beta:  # and self.position.maxPlayer:
                break
            """ elif node.alpha < node.beta and not self.position.maxPlayer:
                break """
        return score
