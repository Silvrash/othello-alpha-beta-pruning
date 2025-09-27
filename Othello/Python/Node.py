from OthelloPosition import OthelloPosition


class Node:
    def __init__(
        self,
        pos: OthelloPosition,
        compute_depth,
        parent=None,
        alpha=-100,
        beta=100,
        time_control=None,
        evaluator=None,
    ):
        self.position = pos
        self.parent = parent
        self.leaf = False
        # self.children = []
        self.alpha = alpha
        self.beta = beta
        self.compute_depth = compute_depth
        self.best_move = None
        self.time_control = time_control
        self.evaluator = evaluator

        # if root
        if self.parent is None:
            self.depth = 0
            # if we play as black, use black evaluator
            self.time_control()
            self.alpha_beta(self)

        else:
            self.depth = self.parent.depth + 1
            # if leaf
            if self.depth == compute_depth:
                self.leaf = True

    def alpha_beta(self, node):
        return self.max(node)

    def max(self, node):
        best_move = None

        if node.leaf:
            self.time_control()
            return node.evaluator.evaluate(node.position)
        score = float("-inf")

        moves = node.position.get_moves()
        # Terminal condition: no legal moves
        if not moves:
            self.time_control()
            return node.evaluator.evaluate(node.position)

        moves.sort(key=node.evaluator.move_priority, reverse=True)

        for m in moves:
            self.time_control()
            new_position = node.position.make_move(m)
            child_node = Node(
                new_position,
                self.compute_depth,
                node,
                node.alpha,
                node.beta,
                evaluator=node.evaluator,
                time_control=self.time_control,
            )

            child_score = self.min(child_node)
            if score < child_score:
                score = child_score
                best_move = m

            node.best_move = best_move

            node.alpha = max(node.alpha, score)
            if node.alpha >= node.beta:
                break
        return score

    def min(self, node):
        best_move = None
        self.time_control()
        if node.leaf:
            self.time_control()
            return node.evaluator.evaluate(node.position)
        score = float("inf")

        moves = node.position.get_moves()
        # Terminal condition: no legal moves
        if not moves:
            self.time_control()
            return node.evaluator.evaluate(node.position)

        moves.sort(key=node.evaluator.move_priority, reverse=True)

        for m in moves:
            self.time_control()
            new_position = node.position.make_move(m)
            child_node = Node(
                new_position,
                self.compute_depth,
                node,
                node.alpha,
                node.beta,
                evaluator=node.evaluator,
                time_control=self.time_control,
            )

            child_score = self.max(child_node)
            if score > child_score:
                score = child_score
                best_move = m
            node.beta = min(node.beta, score)
            node.best_move = best_move
            if node.alpha >= node.beta:
                break
        return score
