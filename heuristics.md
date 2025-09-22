# Othello AI Heuristics Documentation

## Overview

In this document, we describe our heuristic evaluation system used in our Othello AI implementation.
Our primary focus was to maximize stability while minimizing anything that contradicts stability.
In the game of othello, the probability of winning the game increases with more stable discs.


## Core Philosophy

Our design is based on a fundamental principle in the art of war. 
Assuming on the battlefield, there exists a invisible sniper that cannot be shot or taken down even if you are in range
however, once you are in the range of fire, they eliminate you.
In the game, such a sniper is linked to stable discs. Corners are the most stable pieces in the game since they can never be flipped.
We penalize any move that creates a vulnerability that the opponent can exploit.



## Key Heuristic Features

### 1. Stability-Based Evaluation

- **Corner Discs (Weight: 16)**: Corners are the most stable positions on the board. 
Once you capture a corner it can never be flipped and provides a strong foundation to building more stable discs around.
We assigned this feature the highest weight in our evaluation since it increases the probability of winning the game.


- **Stable Discs (Weight: 16)**: These discs can never be flipped in any direction. 
The chances of winning the game increases as a builds more stable pieces.
We calculate this by checking in all directions for opponent pieces.

### 2. Vulnerability Avoidance

- **X-Squares (Weight: 1/16 - Penalty)**: These are the discs diagonally adjacent to corners: (2,2), (2,7), (7,2), (7,7).
Once we play such a move, we are almost certain to give up a corner in the long run. 
As such, we heavily penalize this throughout the game. If playing an X-square can be avoided, we do unless no there are no better moves.


- **C-Squares (Weight: 1/16 - Penalty)**: Squares directly adjacent to corners: (1,2), (2,1), (7,1), (8,2), (8,7), (1,7), (2,8)
Like X-squares, playing this leads to the eventual capture of a corner. We treat these like x-squares but they are not more dangerous than X-squares 


- **Frontier Discs (Weight: 1/4 - Penalty)**: Discs adjacent to empty squares (excluding edges). 
Although the winner is determined by the number of discs a player has, in the early game, having more discs increases the 
chances that your opponent will flip them mid-game and use them to his advantage.
A frontier disc is one that is adjacent to an empty square and an opponent's disc.
Frontier discs are the least stable discs on the board as such, it's best to reduce the number of frontier discs in the early game.
With this in mind, we designed a heuristic that prioritizes the reduction of frontier discs in the early game.


### 3. Positional Control

- **Edge Control (Weight: 4)**: These are squares along the boarders of the board.
C-squares are on the edges but since we penalize them, we do not include them in our edge control evaluation
Having many discs on the edge is advantageous since it leads to capturing a corner, however this could be disadvantageous in the early game
since having too many discs on the edge early in the game increases the chances that your 
opponent will flip them and use them to his advantage.
In our evaluation, we exclude these from the early game stage.


- **Center Control (Weight: 4)**: A strategy employed by Brian Rose, the 2001 World Othello Champion, 
is to have more control of the center during the early stages of the game. These are the 4x4 center area on the board. 
This is because they show their true strength in the late stages of the game when you take control of the corners.
They provide more flexibility and mobility in the game. We used this feature only in the early stage of our game 
to maximize the chances of we winning the center and becoming stable at the center


- **Mobility (Weight: 8)**: As the number of legal moves increases, a player has more options to play than to be forced to play a bad move.


## Game Phase Strategy

In our evaluation, different features are used based on the phase in the game.

### Early Game (< 20 pieces)
**Active Heuristics**:
- Corner control (highest priority)
- Center control
- Mobility
- X-square avoidance (prevent corner loss)
- C-square avoidance (minimize risk)
- Frontier minimization (reduce vulnerability)

### Mid Game (20-45 pieces)
**Active Heuristics**:
- Corner control
- Stable disc building
- Edge control
- Mobility maintenance
- X-square and C-square avoidance
- Frontier minimization

### Late Game (> 45 pieces)
In the late stage, we try to maximize final piece count and stability

**Active Heuristics**:
- Corner control
- Stable disc maximization
- X-square and C-square avoidance
- Frontier management
- Piece count optimization

## Implementation Details

### Move Ordering Priority
In our alpha-beta algorithm, we noticed some good moves were being pruned.
As such, we decided to sort our moves giving priority to stable positions.
This increases the chances of finding our best move earlier

1. **Corner moves**: Priority 1000 (highest)
2. **Edge moves**: Priority 100
3. **Center moves**: Priority 10
4. **Regular moves**: Priority 1
5. **C-square moves**: Priority -500 (penalty)
6. **X-square moves**: Priority -1000 (highest penalty)
7. **Pass moves**: Priority -∞ (only when forced)

### Strategic Effectiveness
- Balances short-term tactics with long-term strategy
- Adapts to different game phases automatically
- Prioritizes stability over immediate piece count
- Minimizes opponent's opportunities for counterplay

## Conclusion

This heuristic system provides a robust foundation for strong Othello play by:
1. Maximizing long-term stability
2. Minimizing tactical vulnerabilities
3. Adapting strategy to game phases
4. Maintaining computational efficiency

The combination of stability-focused evaluation with phase-appropriate weighting creates an AI that plays strategically 
sound Othello while remaining computationally efficient.
