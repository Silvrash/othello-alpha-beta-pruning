from __future__ import annotations
from OthelloPosition import OthelloPosition
from OthelloAction import OthelloAction
from CountingEvaluator import CountingEvaluator

class Node:
    evaluator = CountingEvaluator()

    def __init__(self, pos: OthelloPosition, compute_depth, parent=None, alpha=-100, beta=100):
        self.position = pos
        self.parent = parent
        self.leaf = False
        self.children = []
        self.alpha = alpha
        self.beta = beta
        self.compute_depth = compute_depth
        self.best_move = None

        #if root
        if (self.parent == None):
            self.depth = 0
            self.alpha_beta(self)
        else:
            self.depth = self.parent.depth + 1
            #if leaf
            if(self.depth == compute_depth):
                self.leaf = True
                
    
    def alpha_beta(self, node: Node):
        if node.position.maxPlayer:
            return self.max(node)
        else:
            return self.min(node)
        

    def max(self, node):
        best_move = None

        if(node.leaf == True):
            return Node.evaluator.evaluate(node.position)
        score = -100
        
        moves = node.position.get_moves()
        #pass if no legal moves
        if (moves == []):
            moves = [OthelloAction(0, 0, True)]
        for m in moves:
            new_position = node.position.clone()
            new_position.make_move(m)
            child_node = Node(new_position, self.compute_depth, node, node.alpha, node.beta)
            #do we really need to store them ?
            node.children.append([child_node, m])
            #???????????

            child_score = self.min(child_node)
            if (score < child_score):
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



    def min(self, node):
        best_move = None

        if(node.leaf == True):
            return Node.evaluator.evaluate(node.position)
        score = 100
        
        moves = node.position.get_moves()
        #pass if no legal moves
        if (moves == []):
            moves = [OthelloAction(0, 0, True)]
        for m in moves:
            new_position = node.position.clone()
            new_position.make_move(m)
            child_node = Node(new_position, self.compute_depth, node, node.alpha, node.beta)
            #do we really need to store them ?
            node.children.append([child_node, m])
            #???????????
            child_score = self.max(child_node)
            if (score > child_score):
                score = child_score
                best_move = m
            node.beta = min(node.beta, score)
            node.best_move = best_move
            if node.alpha >= node.beta: #and self.position.maxPlayer:
                break
            """ elif node.alpha < node.beta and not self.position.maxPlayer:
                break """
        return score


    