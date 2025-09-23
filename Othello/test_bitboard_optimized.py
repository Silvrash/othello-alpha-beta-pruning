#!/usr/bin/env python3

from BitboardOthelloPosition import BitboardOthelloPosition
from OthelloAction import OthelloAction

def test_basic_functionality():
    """Test basic bitboard functionality"""
    print("Testing optimized BitboardOthelloPosition...")
    
    # Test initialization
    pos = BitboardOthelloPosition()
    pos.initialize()
    
    print("Initial position:")
    pos.print_board()
    
    # Test move generation
    moves = pos.get_moves()
    print(f"\nInitial moves: {len(moves)}")
    for move in moves:
        print(f"  {move}")
    
    # Test making a move
    if moves:
        first_move = moves[0]
        print(f"\nMaking move: {first_move}")
        new_pos, flip_count = pos.make_move(first_move)
        print(f"Flipped {flip_count} pieces")
        print("After move:")
        new_pos.print_board()
        
        # Test next moves
        next_moves = new_pos.get_moves()
        print(f"\nNext moves: {len(next_moves)}")
        for move in next_moves[:5]:  # Show first 5
            print(f"  {move}")

def test_string_parsing():
    """Test parsing from string"""
    print("\n" + "="*50)
    print("Testing string parsing...")
    
    # Test with a game position
    test_string = "WEEEEEEEEEEEEEEEEEEEEEEEEEEEOXEEEEEEXOEEEEEEEEEEEEEEEEEEEEEEEEEEE"
    pos = BitboardOthelloPosition(test_string)
    
    print("Parsed position:")
    pos.print_board()
    
    moves = pos.get_moves()
    print(f"Available moves: {len(moves)}")
    for move in moves[:8]:  # Show first 8
        print(f"  {move}")

if __name__ == "__main__":
    test_basic_functionality()
    test_string_parsing()
