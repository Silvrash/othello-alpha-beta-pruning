from Node import Node

root = Node(name='root')

a_1 = Node(name='a_1')
a_11 = Node(value=3, name='a_11')
a_12 = Node(value=12, name='a_12')
a_13 = Node(value=8, name='a_13')

a_1.add_child(a_11)
a_1.add_child(a_12)
a_1.add_child(a_13)

a_2 = Node(name='a_2')
a_21 = Node(value=2, name='a_21')
a_22 = Node(value=4, name='a_22')
a_23 = Node(value=6, name='a_23')

a_2.add_child(a_21)
a_2.add_child(a_22)
a_2.add_child(a_23)

a_3 = Node(name='a_3')
a_31 = Node(value=14, name='a_31')
a_32 = Node(value=5, name='a_32')
a_33 = Node(value=2, name='a_33')

a_3.add_child(a_31)
a_3.add_child(a_32)
a_3.add_child(a_33)


root.add_child(a_1)
root.add_child(a_2)
root.add_child(a_3)


# # Level 1: Min nodes (3 nodes)
# min_node_1 = Node(name="min_node_1")
# min_node_2 = Node(name="min_node_2")
# min_node_3 = Node(name="min_node_3")

# # Level 2: Max nodes (7 nodes total)
# # Under min_node_1: 2 max nodes
# max_node_1_1 = Node(name="max_node_1_1")
# max_node_1_2 = Node(name="max_node_1_2")
# # Under min_node_2: 3 max nodes
# max_node_2_1 = Node(name="max_node_2_1")
# max_node_2_2 = Node(name="max_node_2_2")
# max_node_2_3 = Node(name="max_node_2_3")

# # Under min_node_3: 2 max nodes
# max_node_3_1 = Node(name="max_node_3_1")
# max_node_3_2 = Node(name="max_node_3_2")

# # Level 3: Leaf nodes with values from the image
# # Under max_node_1_1: values 2, 3
# leaf_1_1_1 = Node(name="leaf_1_1_1", value=2)
# leaf_1_1_2 = Node(name="leaf_1_1_2", value=3)

# # Under max_node_1_2: values 5, 1
# leaf_1_2_1 = Node(name="leaf_1_2_1", value=5)
# leaf_1_2_2 = Node(name="leaf_1_2_2", value=1)

# # Under max_node_2_1: value 0
# leaf_2_1_1 = Node(name="leaf_2_1_1", value=0)

# # Under max_node_2_2: values -5, 7
# leaf_2_2_1 = Node(name="leaf_2_2_1", value=-5)
# leaf_2_2_2 = Node(name="leaf_2_2_2", value=7)

# # Under max_node_2_3: values 2, 1
# leaf_2_3_1 = Node(name="leaf_2_3_1", value=2)
# leaf_2_3_2 = Node(name="leaf_2_3_2", value=1)

# # Under max_node_3_1: value 3
# leaf_3_1_1 = Node(name="leaf_3_1_1", value=3)

# # Under max_node_3_2: value 9
# leaf_3_2_1 = Node(name="leaf_3_2_1", value=9)

# # Build the tree structure
# # Level 3 to Level 2
# max_node_1_1.add_child(leaf_1_1_1)
# max_node_1_1.add_child(leaf_1_1_2)

# max_node_1_2.add_child(leaf_1_2_1)
# max_node_1_2.add_child(leaf_1_2_2)

# max_node_2_1.add_child(leaf_2_1_1)

# max_node_2_2.add_child(leaf_2_2_1)
# max_node_2_2.add_child(leaf_2_2_2)

# max_node_2_3.add_child(leaf_2_3_1)
# max_node_2_3.add_child(leaf_2_3_2)

# max_node_3_1.add_child(leaf_3_1_1)

# max_node_3_2.add_child(leaf_3_2_1)

# # Level 2 to Level 1
# min_node_1.add_child(max_node_1_1)
# min_node_1.add_child(max_node_1_2)

# min_node_2.add_child(max_node_2_1)
# min_node_2.add_child(max_node_2_2)
# min_node_2.add_child(max_node_2_3)

# min_node_3.add_child(max_node_3_1)
# min_node_3.add_child(max_node_3_2)

# # Level 1 to Root
# root.add_child(min_node_1)
# root.add_child(min_node_2)
# root.add_child(min_node_3)

def minimax_alpha_beta(node: Node, max_depth):
    return max_value(node, float("-inf"), float("inf"), max_depth)


def max_value(node: Node, alpha: float, beta: float, max_depth):
    children = node.children
    if len(children) == 0 or node.depth >= max_depth:
        return node

    best_child = Node(value=float("-inf"))

    for index, _ in enumerate(children):
        child = children[index]
        best_child = max(best_child, min_value(child, alpha, beta, max_depth - 1), key= lambda x: x.value)

        alpha = max(alpha, best_child.value)
        if alpha >= beta:
            node.children = node.children[:index + 1]
            break

    node.set_best_child(best_child)
    return node


def min_value(node: Node, alpha: float, beta: float, max_depth: int):
    if len(node.children) == 0:
        return node

    best_child = Node(value=float("inf"))

    for index, _ in enumerate(node.children):
        child = node.children[index]
        best_child = min(best_child, max_value(child, alpha, beta, max_depth - 1), key=lambda x: x.value)

        beta = min(beta, best_child.value)
        if alpha >= beta:
            node.children = node.children[:index + 1]
            break

    node.set_best_child(best_child)
    return node


root  = minimax_alpha_beta(root, 3)
root.print_tree()
