#!/usr/bin/env python3
"""
HeuristicEvaluator: Strategic Othello Position Evaluator

This module implements a sophisticated position evaluator for Othello that uses
optimized feature weights to assess board positions. The evaluator combines multiple
strategic features including mobility, corner control, stability, and positional
advantages to provide accurate position assessments.

The evaluator is designed to work with the Alpha-Beta pruning algorithm and
provides move prioritization for optimal search efficiency.

Key Features:
- 10 strategic features extracted from board positions
- Optimized weights determined through strategic analysis
- Mobility-focused strategy to counter naive opponents
- Efficient numpy-based computations
- Move prioritization for alpha-beta optimization

Author: Afrasah Benjamin Arko
"""

import numpy as np
from typing import Optional
from OthelloEvaluator import OthelloEvaluator
from OthelloPosition import OthelloPosition
from FeatureExtractor import FeatureExtractor


class HeuristicEvaluator(OthelloEvaluator):
    """
    Strategic evaluator for othello game play.
    
    This evaluator uses a comprehensive set of 10 strategic features to assess
    Othello board positions. The weights for these features have been optimized
    through game theory principles and strategic analysis.
    
    The evaluator implements a mobility-dominant strategy that prioritizes:
    - Corner control (highest weight: 600.0)
    - Mobility and potential mobility
    - Stability and positional advantages
    - Penalties for dangerous squares (X-squares, C-squares)
    
    Attributes:
        feature_extractor (FeatureExtractor): Extracts strategic features from positions
        weights (np.ndarray): Optimized weights for each feature (10 features)

    """

    def __init__(self, playing_white: bool) -> None:
        self.feature_extractor = FeatureExtractor(playing_white)
        self.weights: Optional[np.ndarray] = None
        self.bias: float = 0.0
        self.playing_white: bool = playing_white

        self._initialize_default_weights()

    def _initialize_default_weights(self) -> None:
        """
        Initialize the evaluator with mobility-dominant default weights.
        
        These weights have been optimized through strategic analysis and
        are designed to implement a strong Othello strategy by emphasizing mobility
        and corner control while avoiding dangerous square occupations.
        
        Weight breakdown:
        - piece_diff (100.0): Moderate importance for piece count
        - mobility_diff (100.0): High importance for current move options
        - corner_diff (600.0): Highest importance for corner control
        - x_square_diff (-50.0): High penalty for dangerous X-squares
        - c_square_diff (-5.0): Moderate penalty for C-squares
        - edge_diff (70.0): Good importance for edge control
        - frontier_diff (-10.0): Penalty for vulnerable frontier pieces
        - parity_score (18.0): Tempo advantage consideration
        - stability_diff (90.0): High importance for piece stability
        - potential_mobility_diff (6.0): Future move potential
        """
        # Mobility-dominant weights optimized for strategic play
        self.weights = np.array([
            100.0,  # piece_diff - moderate importance
            100.0,  # mobility_diff - high importance for current moves
            600.0,  # corner_diff - highest importance for stability
            -50.0,  # x_square_diff - high penalty for dangerous squares
            -5.0,   # c_square_diff - moderate penalty for risky squares
            70.0,   # edge_diff - good importance for edge control
            -10,     # frontier_diff - penalty for vulnerable pieces
            18,     # parity_score - tempo advantage consideration
            90.0,   # stability_diff - high importance for piece stability
            6,      # potential_mobility_diff - future move potential
        ])
        self.bias = 1.0

    def evaluate(self, othello_position: OthelloPosition) -> float:
        """
        Evaluate an Othello position using optimized feature weights.
        
        This method extracts 10 strategic features from the given position
        and computes a weighted linear combination to produce the final
        evaluation score. Positive scores favor the starting player (white if
        playing_white=True), while negative scores favor the opponent.
        
        Args:
            othello_position (OthelloPosition): The board position to evaluate.
                                               Must be a valid Othello position.
        
        Returns:
            float: Evaluation score where:
                   - Positive values favor the starting player
                   - Negative values favor the opponent
                   - Magnitude indicates strength of advantage
        """
        # Extract strategic features from the position
        features = self.feature_extractor.extract_features(othello_position)
        
        # Compute weighted linear combination
        score = np.dot(self.weights, features) + self.bias
        
        return score

