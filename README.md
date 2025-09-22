# Othello Alpha-Beta Pruning AI

An intelligent Othello (Reversi) game implementation using Alpha-Beta pruning algorithm with advanced heuristics for optimal move selection.

## Overview

This project implements a sophisticated Othello AI player that uses the Alpha-Beta pruning algorithm combined with iterative deepening search and advanced positional heuristics. The AI is designed to make optimal moves within given time constraints while maximizing winning chances.

## Features

- **Alpha-Beta Pruning**: Efficient minimax search with alpha-beta pruning for optimal performance
- **Iterative Deepening**: Progressive depth search to maximize search depth within time limits
- **Advanced Heuristics**: Multi-factor evaluation system considering:
  - Corner control (highest priority)
  - X-squares and C-squares avoidance
  - Edge control
  - Center control
  - Mobility (number of legal moves)
  - Stable discs (pieces that cannot be flipped)
  - Frontier squares
- **Time Management**: Intelligent time allocation with 99% buffer for evaluation overhead
- **Move Ordering**: Priority-based move sorting to improve alpha-beta pruning efficiency

## Installation & Usage

### Prerequisites
- Python 3.7+
- NumPy

### Running the AI

1. **Basic Usage**:
   ```bash
   python Othello/Othello.py [position_string] [time_limit]
   ```

2. **Using the provided script**:
   ```bash
   ./run.sh
   ```

3. **Time range testing**:
   ```bash
   ./run_time_range.sh
   ```

### Input Format

- **Position String**: 65-character string where:
  - First character: 'W' (White to move) or 'B' (Black to move)
  - Next 64 characters: Board state ('E'=Empty, 'O'=White, 'X'=Black)
- **Time Limit**: Maximum search time in seconds

### Example

```bash
python Othello/Othello.py "BEXEXOOOXEEXXOEXEEEEOOXOEEEOOOEEEEOOOOEEEEEXOEEEEEEEEEEEEEEEEEEEE" 5.0
```

## Algorithm Details

### Alpha-Beta Pruning

The implementation uses a recursive alpha-beta pruning algorithm with:
- **Max nodes**: Maximize score for the current player
- **Min nodes**: Minimize score for the opponent
- **Alpha cutoff**: Stop searching when alpha ≥ beta
- **Beta cutoff**: Stop searching when beta ≤ alpha

### Iterative Deepening

The search progressively increases depth:
1. Start with depth 1
2. Search to current depth within time limit
3. Increment depth and repeat
4. Return best move from deepest completed search

### Heuristic Evaluation

The `PrimaryEvaluator` uses a sophisticated multi-factor system:

#### Game Phases
- **Early Game** (< 20 pieces): Focus on mobility, center control, corner avoidance
- **Mid Game** (20-45 pieces): Balance of all factors
- **Late Game** (> 45 pieces): Focus on piece count and stability

#### Positional Weights
- **Corners**: Weight 16 (highest priority)
- **Stable Discs**: Weight 16
- **Mobility**: Weight 8
- **Edge Squares**: Weight 4
- **Center Control**: Weight 4
- **Frontier Squares**: Weight 0.25 (penalty)
- **X-Squares**: Weight 0.0625 (penalty)
- **C-Squares**: Weight 0.0625 (penalty)

## Performance Optimizations

1. **Move Ordering**: Moves sorted by priority to improve pruning
2. **Vectorized Operations**: NumPy-based calculations for speed
3. **Time Management**: 99% time buffer prevents timeout
4. **Recursion Limits**: Optimized for Othello's branching factor

## Testing

The project includes comprehensive testing with:
- Time range analysis (2-10 seconds)
- Performance logging
- Game result tracking

Test results are stored in `time_range_logs/` directory.

## Authors

- **Afrasah Benjamin Arko**
- **Sienichev Matvey**

Based on original framework by **Ola Ringdahl**

## License

This project is part of the 5DV243 Artificial Intelligence course assignments.
