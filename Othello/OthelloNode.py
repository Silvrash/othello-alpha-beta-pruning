from __future__ import annotations
from typing import List

from OthelloPosition import OthelloPosition
from OthelloAction import OthelloAction

class OthelloNode(object):
  """
  This class represents a node in the game tree.
  action: the action applied to get to this node
  state: state of the game at this node
  depth: depth at which the node was found
  parent: previous node
  """
  def __init__(self, state: OthelloPosition, depth: int=0, action: OthelloAction=None, parent: OthelloNode = None):
    self.action = action or OthelloAction(0, 0, True)
    self.state = state if not parent else state.clone().make_move(action)
    self.parent = parent
    self.depth = depth

  def __iter__(self):
    yield self
    for child in self.children:
      yield from child


  def _repr_with_indent(self, indent_level: int) -> str:
    """
    Helper method to create indented representation for tree structure.
    """
    indent = "  " * indent_level
    
    node_str = f"{indent}{self}"

    if len(self.children):
      children_str = "\n".join(child._repr_with_indent(indent_level + 1) for child in self.children)
      return f"{node_str}\n{children_str}"
    else:
      return node_str
  
  def __str__(self) -> str:
    """
    Returns a concise string representation of the node.
    """
    action_str = str(self.action) if self.action else "ROOT"
    node_score = self.action.value if self.action else 0
    parent_score = self.parent.action.value if self.parent and self.parent.action else 0
    player_str = "W" if self.state.maxPlayer else "B"
    return f"Node({action_str}, {player_str}, d={self.depth}, score={node_score}, parent_score={parent_score})"

  def print_tree(self):
    print(self._repr_with_indent(self.depth))

  