import pandas as pd
import numpy as np

def validate_weights(weights, criteria_count=5):
    """Validate and normalize weights"""
    if len(weights) != criteria_count:
        raise ValueError(f"Expected {criteria_count} weights, got {len(weights)}")
    
    weights = np.array(weights)
    if np.any(weights < 0):
        raise ValueError("Weights cannot be negative")
    
    # Normalize to sum to 1
    if np.sum(weights) == 0:
        raise ValueError("Weights cannot all be zero")
    
    return weights / np.sum(weights)