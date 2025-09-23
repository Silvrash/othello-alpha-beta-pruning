from BitboardOthelloPosition import BitboardOthelloPosition
from OthelloAction import OthelloAction

posString = "BEEEEEEEEEEEEOEOEEEOOXOEEEEOOXEEEEEOOXEEEEEEEXEEEEEEEEEEEEEEEEEEE"

pos = BitboardOthelloPosition(posString)

pos.print_board()

pos, flip_count = pos.make_move(OthelloAction(1, 8))

pos.print_board()

print(flip_count)