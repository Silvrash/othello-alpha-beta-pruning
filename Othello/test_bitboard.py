#!/usr/bin/env python3
"""
Test script to validate the bitboard implementation against the original OthelloPosition.
This ensures that the bitboard version produces identical results.
"""

import sys
import time
from OthelloPosition import OthelloPosition
from BitboardOthelloPosition import BitboardOthelloPosition
from OthelloAction import OthelloAction


def test_position_equivalence(pos_str):
    """Test that both implementations produce the same results for a given position"""
    print(f"Testing position: {pos_str[:20]}...")
    
    # Create both positions
    original_pos = OthelloPosition(pos_str)
    bitboard_pos = BitboardOthelloPosition(pos_str)
    
    # Test move generation
    original_moves = set(str(move) for move in original_pos.get_moves())
    bitboard_moves = set(str(move) for move in bitboard_pos.get_moves())
    
    if original_moves != bitboard_moves:
        print(f"❌ Move generation mismatch!")
        print(f"Original moves: {sorted(original_moves)}")
        print(f"Bitboard moves: {sorted(bitboard_moves)}")
        return False
    
    print(f"✅ Move generation matches ({len(original_moves)} moves)")
    
    # Test a few moves if there are any
    if original_moves:
        # Test first move
        first_move_str = sorted(original_moves)[0]
        # Parse move string to create OthelloAction
        if first_move_str != "pass":
            coords = first_move_str.strip("()").split(",")
            row, col = int(coords[0]), int(coords[1])
            move = OthelloAction(row, col)
            
            # Test make_move
            try:
                original_new = original_pos.make_move(move)
                bitboard_new = bitboard_pos.make_move(move)
                
                # Compare resulting positions
                original_moves_after = set(str(m) for m in original_new.get_moves())
                bitboard_moves_after = set(str(m) for m in bitboard_new.get_moves())
                
                if original_moves_after != bitboard_moves_after:
                    print(f"❌ Position after move mismatch!")
                    print(f"Original moves after: {sorted(original_moves_after)}")
                    print(f"Bitboard moves after: {sorted(bitboard_moves_after)}")
                    return False
                    
                print(f"✅ Position after move matches")
                
            except Exception as e:
                print(f"❌ Error during move execution: {e}")
                return False
    
    return True


def test_performance():
    """Test performance improvement of bitboard implementation"""
    print("\n=== Performance Test ===")
    
    # Test position with many moves
    test_pos = "BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE"
    
    original_pos = OthelloPosition(test_pos)
    bitboard_pos = BitboardOthelloPosition(test_pos)
    
    # Warm up
    for _ in range(10):
        original_pos.get_moves()
        bitboard_pos.get_moves()
    
    # Test original implementation
    start_time = time.time()
    for _ in range(1000):
        moves = original_pos.get_moves()
    original_time = time.time() - start_time
    
    # Test bitboard implementation
    start_time = time.time()
    for _ in range(1000):
        moves = bitboard_pos.get_moves()
    bitboard_time = time.time() - start_time
    
    print(f"Original implementation: {original_time:.4f}s for 1000 calls")
    print(f"Bitboard implementation: {bitboard_time:.4f}s for 1000 calls")
    print(f"Speedup: {original_time / bitboard_time:.2f}x")
    
    return bitboard_time < original_time


def main():
    """Run comprehensive tests"""
    print("=== Bitboard Othello Implementation Test ===")
    
    # Test cases
    test_positions = [
        # Initial position
        "WEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE",
        # Position with some pieces
        "BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE",
        # Position with more pieces
        "WOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO",
        # Position with mixed pieces
        "BXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOOXXOO",
    ]
    
    all_passed = True
    
    # Test equivalence
    for pos in test_positions:
        if not test_position_equivalence(pos):
            all_passed = False
        print()
    
    # Test performance
    if all_passed:
        performance_improved = test_performance()
        if performance_improved:
            print("✅ Performance test passed - bitboard is faster!")
        else:
            print("⚠️  Performance test failed - bitboard is not faster")
    else:
        print("❌ Skipping performance test due to equivalence failures")
    
    if all_passed:
        print("\n🎉 All tests passed! Bitboard implementation is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)


if __name__ == "__main__":
    main()
