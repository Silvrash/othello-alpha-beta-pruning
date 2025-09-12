from OthelloAction import OthelloAction
from OthelloPosition import OthelloPosition
from CountingEvaluator import CountingEvaluator

import os
os.system('cls' if os.name == 'nt' else 'clear')

position = OthelloPosition('BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE')

position.print_board()

evaluator = CountingEvaluator()
while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    position.print_board()

    print(f"score: {evaluator.evaluate(position)}")

    print(f'possible moves for {"white" if position.maxPlayer else "black"}:', position.get_moves())
    move = input('Enter move (row, col): ')
    row, col = map(int, move.split(','))
    position = position.make_move(OthelloAction(row, col))

    if len(position.get_moves()) == 0:
        position.maxPlayer = not position.maxPlayer
        print(f'{"white" if position.maxPlayer else "black"} makes a pass move')
        print(f'state f{position.board}')
        position.print_board()
        continue