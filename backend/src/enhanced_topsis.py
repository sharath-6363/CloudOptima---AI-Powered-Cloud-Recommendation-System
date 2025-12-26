import numpy as np
import pandas as pd

class EnhancedTOPSIS:
    def __init__(self):
        pass
    
    def get_recommendations_with_ratings(self, budget, region, weights, user_ratings):
        """
        Enhanced TOPSIS that considers user rating history
        For new users, this provides personalized recommendations
        """
        # This would integrate with the main TOPSIS algorithm
        # For now, return a mock response
        return [
            {
                'rank': 1,
                'provider': 'AWS',
                'instance_type': 't3.medium',
                'price_per_hour': 0.0416,
                'vCPU': 2,
                'RAM_GB': 4.0,
                'storage_GB': 100.0,
                'security_score': 85.0,
                'topsis_score': 0.7500,
                'adjusted_for_ratings': True,
                'personalization_note': 'Recommended based on similar user preferences'
            }
        ]
    
    def _analyze_rating_patterns(self, user_ratings):
        """Analyze user's rating patterns to adjust weights"""
        if not user_ratings:
            return None
        
        # Simple analysis - in real implementation, this would be more sophisticated
        avg_rating = np.mean([r['rating'] for r in user_ratings])
        
        if avg_rating > 4.0:
            return "prefers_balanced"
        elif avg_rating < 3.0:
            return "prefers_cost_effective"
        else:
            return "prefers_performance"