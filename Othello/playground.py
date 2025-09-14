from AlphaBeta import AlphaBeta, StopSignal
from OthelloNode import OthelloNode
from OthelloAction import OthelloAction
from OthelloPosition import OthelloPosition
from CountingEvaluator import CountingEvaluator

import os

os.system("cls" if os.name == "nt" else "clear")


def make_best_move(root, time_limit):
    best_move = None
    depth = 1
    # Which evaluator (heuristics) should be used
    algorithm = AlphaBeta(CountingEvaluator())
    algorithm.set_time_limit(time_limit)

    while True:
        # Set the depth that AlphaBeta will search to.
        algorithm.set_search_depth(depth)

        # Evaluate the position
        try:
            move = algorithm.evaluate(root)

            if not best_move or move.value > best_move.value:
                best_move = move

            depth += 1

        except StopSignal:
            # time expired
            break
    return best_move


position = OthelloPosition()
position.initialize()


evaluator = CountingEvaluator()

position.print_board()

skip_count = 0

while True:
    print("\n")
    root = OthelloNode(state=position, depth=0)
    move = make_best_move(root, 1)
    position.make_move(move)
    position.print_board()
    
    # If we have remaining skip count, decrement and continue
    if skip_count > 0:
        skip_count -= 1
        print(f"\nSkipping... ({skip_count} moves remaining)")
        continue
    
    val = input("\nEnter number to skip or press enter to continue:")
    
    # Check if input is a number
    if val.strip().isdigit():
        skip_count = int(val.strip())
        print(f"Skipping {skip_count} moves...")
        skip_count -= 1  # Decrement since we're about to continue
    else:
        print("Invalid input. Continuing normally...")

    

