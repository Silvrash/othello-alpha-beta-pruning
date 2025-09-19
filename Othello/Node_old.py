from __future__ import annotations
from typing import List
from OthelloPosition import OthelloPosition
from OthelloAction import OthelloAction


class Node(OthelloAction):
    """
    This class represents a node in the game tree.
    action: the action applied to get to this node
    state: state of the game at this node
    depth: depth at which the node was found
    parent: previous node
    """

    def __init__(
        self,
        row=None,
        col=None,
        is_pass_move=None,
        othello_position: OthelloPosition=None,
        value=float("-inf"),
        name=None,
    ):
        super().__init__(row, col, is_pass_move)
        self.name = name
        self.othello_position = othello_position
        self.depth = 1
        self.parent = None
        self.best_child = None
        self.value = value
        self.children: List[Node] = []

    # @property
    # def children(self):
    #     return self.othello_position.get_moves()

    def set_depth(self, depth):
        self.depth = depth

    def add_child(self, node: Node):
        node.depth = self.depth + 1
        node.parent = self
        self.children.append(node)

    def set_best_child(self, node: Node):
        self.best_child = node
        self.value = node.value

    def _update_descendant_depths(self, node: Node):
        """Recursively update depths of all descendants"""
        for child in node.children:
            child.depth = node.depth + 1
            self._update_descendant_depths(child)

    def print_tree(self, level=0):
        """Print the tree structure starting from this node"""
        indent = "  " * level
        print(
            f"{indent}Node(depth={self.depth}, name={self.name}, value={self.value}, best_child={self.best_child.name if self.best_child else None})"
        )

        for child in self.children:
            child.print_tree(level + 1)

    def __str__(self) -> str:
        """
        Returns a concise string representation of the node.
        """
        return f"Node(depth={self.depth}, value={self.value},children={len(self.children)}, best_child={self.best_child.name if self.best_child else None})"
