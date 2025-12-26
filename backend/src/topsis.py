import numpy as np
from scipy.spatial.distance import euclidean
from typing import List, Tuple

class TOPSIS:
    """
    Enhanced TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution)
    Improved accuracy with better normalization and distance calculations
    """
    
    def __init__(self):
        """Initialize TOPSIS with configuration"""
        self.epsilon = 1e-10  # Small value to prevent division by zero
        print("✅ Enhanced TOPSIS initialized")
    
    @staticmethod
    def normalize_matrix(matrix: np.ndarray) -> np.ndarray:
        """
        Normalize decision matrix using vector normalization (improved method)
        
        Each column is normalized by dividing by the square root of sum of squares
        This ensures all criteria are on comparable scales
        
        Args:
            matrix: Decision matrix (alternatives x criteria)
            
        Returns:
            Normalized matrix
        """
        # Convert to float64 for better precision
        matrix = np.asarray(matrix, dtype=np.float64)
        
        # Calculate column-wise norms (Euclidean norm)
        # norm = sqrt(sum(x_i^2))
        column_norms = np.sqrt(np.sum(matrix ** 2, axis=0))
        
        # Avoid division by zero
        column_norms = np.where(column_norms == 0, 1e-10, column_norms)
        
        # Normalize: x_normalized = x / norm
        normalized = matrix / column_norms
        
        return normalized
    
    @staticmethod
    def apply_weights(normalized_matrix: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """
        Apply criteria weights to normalized matrix
        
        Args:
            normalized_matrix: Normalized decision matrix
            weights: Weight vector for each criterion
            
        Returns:
            Weighted normalized matrix
        """
        weights = np.asarray(weights, dtype=np.float64)
        
        # Ensure weights sum to 1
        weights = weights / np.sum(weights)
        
        # Apply weights using broadcasting
        weighted_matrix = normalized_matrix * weights
        
        return weighted_matrix
    
    @staticmethod
    def compute_ideal_solutions(
        weighted_matrix: np.ndarray, 
        criteria_types: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute ideal best and ideal worst solutions (IMPROVED)
        
        - Benefit criteria: max is best, min is worst
        - Cost criteria: min is best, max is worst
        
        Args:
            weighted_matrix: Weighted normalized matrix
            criteria_types: List of 'benefit' or 'cost' for each criterion
            
        Returns:
            Tuple of (ideal_best, ideal_worst) arrays
        """
        criteria_array = np.array(criteria_types)
        
        # Initialize arrays
        ideal_best = np.zeros(weighted_matrix.shape[1])
        ideal_worst = np.zeros(weighted_matrix.shape[1])
        
        # For each criterion
        for j in range(weighted_matrix.shape[1]):
            if criteria_array[j] == 'benefit':
                # Benefit: higher is better
                ideal_best[j] = np.max(weighted_matrix[:, j])
                ideal_worst[j] = np.min(weighted_matrix[:, j])
            else:  # 'cost'
                # Cost: lower is better
                ideal_best[j] = np.min(weighted_matrix[:, j])
                ideal_worst[j] = np.max(weighted_matrix[:, j])
        
        return ideal_best, ideal_worst
    
    @staticmethod
    def compute_distances(
        weighted_matrix: np.ndarray,
        ideal_best: np.ndarray,
        ideal_worst: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute Euclidean distances to ideal solutions (IMPROVED ACCURACY)
        
        Uses proper Euclidean distance formula:
        d = sqrt(sum((x_i - y_i)^2))
        
        Args:
            weighted_matrix: Weighted normalized matrix
            ideal_best: Ideal best solution
            ideal_worst: Ideal worst solution
            
        Returns:
            Tuple of (distances_to_best, distances_to_worst)
        """
        n_alternatives = weighted_matrix.shape[0]
        
        # Compute distances to ideal best
        distances_to_best = np.zeros(n_alternatives)
        for i in range(n_alternatives):
            distances_to_best[i] = euclidean(weighted_matrix[i], ideal_best)
        
        # Compute distances to ideal worst
        distances_to_worst = np.zeros(n_alternatives)
        for i in range(n_alternatives):
            distances_to_worst[i] = euclidean(weighted_matrix[i], ideal_worst)
        
        return distances_to_best, distances_to_worst
    
    @staticmethod
    def compute_closeness_scores(
        distances_to_best: np.ndarray,
        distances_to_worst: np.ndarray,
        epsilon: float = 1e-10
    ) -> np.ndarray:
        """
        Compute relative closeness to ideal solution (IMPROVED)
        
        Closeness = D_worst / (D_best + D_worst)
        
        Score ranges from 0 to 1:
        - 1.0 = closest to ideal best (best option)
        - 0.0 = closest to ideal worst (worst option)
        
        Args:
            distances_to_best: Distances to ideal best
            distances_to_worst: Distances to ideal worst
            epsilon: Small value to prevent division by zero
            
        Returns:
            Closeness scores (0-1)
        """
        # Calculate denominator with safety check
        denominator = distances_to_best + distances_to_worst
        
        # Avoid division by zero
        denominator = np.where(denominator < epsilon, epsilon, denominator)
        
        # Calculate closeness coefficient
        closeness = distances_to_worst / denominator
        
        # Ensure scores are in [0, 1] range
        closeness = np.clip(closeness, 0.0, 1.0)
        
        return closeness
    
    def run_topsis(
        self,
        matrix: np.ndarray,
        weights: List[float],
        criteria_types: List[str]
    ) -> np.ndarray:
        """
        Run complete TOPSIS analysis with improved accuracy
        
        Steps:
        1. Normalize decision matrix
        2. Apply weights
        3. Determine ideal best and worst solutions
        4. Calculate distances
        5. Compute relative closeness scores
        
        Args:
            matrix: Decision matrix (alternatives x criteria)
            weights: Weight for each criterion (must sum to 1 or will be normalized)
            criteria_types: 'benefit' or 'cost' for each criterion
            
        Returns:
            TOPSIS scores for each alternative (0-1, higher is better)
        """
        
        print(f"\n{'='*60}")
        print(f"RUNNING ENHANCED TOPSIS ANALYSIS")
        print(f"{'='*60}")
        
        # Convert inputs to numpy arrays with high precision
        matrix = np.asarray(matrix, dtype=np.float64)
        weights = np.asarray(weights, dtype=np.float64)
        
        # Input validation
        n_alternatives, n_criteria = matrix.shape
        print(f"📊 Input Matrix: {n_alternatives} alternatives × {n_criteria} criteria")
        
        if len(weights) != n_criteria:
            print(f"⚠️ Warning: Adjusting weights from {len(weights)} to {n_criteria}")
            if len(weights) < n_criteria:
                # Pad with equal weights
                additional = n_criteria - len(weights)
                weights = np.concatenate([weights, np.full(additional, 1.0/n_criteria)])
            else:
                weights = weights[:n_criteria]
        
        if len(criteria_types) != n_criteria:
            print(f"⚠️ Warning: Adjusting criteria types from {len(criteria_types)} to {n_criteria}")
            if len(criteria_types) < n_criteria:
                # Assume remaining are benefit criteria
                criteria_types = criteria_types + ['benefit'] * (n_criteria - len(criteria_types))
            else:
                criteria_types = criteria_types[:n_criteria]
        
        # Normalize weights
        weights = weights / np.sum(weights)
        print(f"⚖️ Normalized Weights: {weights}")
        print(f"📋 Criteria Types: {criteria_types}")
        
        # STEP 1: Normalize decision matrix
        print(f"\n🔄 Step 1: Normalizing decision matrix...")
        normalized_matrix = self.normalize_matrix(matrix)
        print(f"✅ Matrix normalized (range: {normalized_matrix.min():.6f} to {normalized_matrix.max():.6f})")
        
        # STEP 2: Apply weights
        print(f"\n🔄 Step 2: Applying criterion weights...")
        weighted_matrix = self.apply_weights(normalized_matrix, weights)
        print(f"✅ Weights applied (range: {weighted_matrix.min():.6f} to {weighted_matrix.max():.6f})")
        
        # STEP 3: Determine ideal solutions
        print(f"\n🔄 Step 3: Computing ideal best and worst solutions...")
        ideal_best, ideal_worst = self.compute_ideal_solutions(weighted_matrix, criteria_types)
        print(f"✅ Ideal Best: {ideal_best}")
        print(f"✅ Ideal Worst: {ideal_worst}")
        
        # STEP 4: Calculate distances
        print(f"\n🔄 Step 4: Calculating Euclidean distances...")
        dist_to_best, dist_to_worst = self.compute_distances(weighted_matrix, ideal_best, ideal_worst)
        print(f"✅ Distance to Best - Min: {dist_to_best.min():.6f}, Max: {dist_to_best.max():.6f}, Avg: {dist_to_best.mean():.6f}")
        print(f"✅ Distance to Worst - Min: {dist_to_worst.min():.6f}, Max: {dist_to_worst.max():.6f}, Avg: {dist_to_worst.mean():.6f}")
        
        # STEP 5: Compute closeness scores
        print(f"\n🔄 Step 5: Computing relative closeness scores...")
        closeness_scores = self.compute_closeness_scores(dist_to_best, dist_to_worst, self.epsilon)
        print(f"✅ TOPSIS Scores - Min: {closeness_scores.min():.6f}, Max: {closeness_scores.max():.6f}, Avg: {closeness_scores.mean():.6f}")
        
        # Show top 5 scores
        top_5_indices = np.argsort(closeness_scores)[-5:][::-1]
        print(f"\n🏆 Top 5 TOPSIS Scores:")
        for i, idx in enumerate(top_5_indices, 1):
            print(f"   #{i}: Alternative {idx} - Score: {closeness_scores[idx]:.6f}")
        
        print(f"{'='*60}")
        print(f"✅ TOPSIS ANALYSIS COMPLETED")
        print(f"{'='*60}\n")
        
        return closeness_scores
    
    def sensitivity_analysis(
        self,
        matrix: np.ndarray,
        weights: List[float],
        criteria_types: List[str],
        weight_variations: float = 0.1
    ) -> dict:
        """
        Perform sensitivity analysis on TOPSIS results
        Tests how results change with weight variations
        
        Args:
            matrix: Decision matrix
            weights: Original weights
            criteria_types: Criteria types
            weight_variations: Percentage to vary weights (default 10%)
            
        Returns:
            Dictionary with sensitivity analysis results
        """
        
        original_scores = self.run_topsis(matrix, weights, criteria_types)
        original_ranking = np.argsort(original_scores)[::-1]
        
        results = {
            'original_scores': original_scores,
            'original_ranking': original_ranking,
            'variations': []
        }
        
        # Test variations for each weight
        weights_array = np.array(weights)
        for i in range(len(weights)):
            # Increase weight
            varied_weights = weights_array.copy()
            varied_weights[i] *= (1 + weight_variations)
            varied_weights = varied_weights / np.sum(varied_weights)
            
            varied_scores = self.run_topsis(matrix, varied_weights, criteria_types)
            varied_ranking = np.argsort(varied_scores)[::-1]
            
            results['variations'].append({
                'criterion': i,
                'direction': 'increase',
                'scores': varied_scores,
                'ranking': varied_ranking,
                'ranking_change': not np.array_equal(original_ranking[:3], varied_ranking[:3])
            })
        
        return results


# Testing function
def test_topsis():
    """Test enhanced TOPSIS implementation"""
    
    print("\n" + "="*60)
    print("TESTING ENHANCED TOPSIS")
    print("="*60)
    
    # Example decision matrix (5 alternatives, 7 criteria)
    # Criteria: price, performance, security, availability, bandwidth, latency, cost_efficiency
    decision_matrix = np.array([
        [0.0530, 85.2, 90, 100, 7, 1.17, 0.0265],  # AWS t3.micro
        [0.0475, 75.1, 90, 100, 7, 1.33, 0.0238],  # AWS t3.nano
        [0.0520, 82.5, 88, 98, 7, 1.25, 0.0520],   # Azure B1s
        [0.0420, 78.3, 92, 99, 7, 1.20, 0.0420],   # GCP e2-micro
        [0.1060, 120.5, 90, 100, 9, 0.95, 0.0530]  # AWS t3.small
    ])
    
    # Weights (must sum to 1 or will be normalized)
    weights = [0.25, 0.20, 0.20, 0.15, 0.10, 0.05, 0.05]
    
    # Criteria types
    criteria_types = ['cost', 'benefit', 'benefit', 'benefit', 'benefit', 'cost', 'cost']
    
    # Run TOPSIS
    topsis = TOPSIS()
    scores = topsis.run_topsis(decision_matrix, weights, criteria_types)
    
    # Display results
    alternatives = ['AWS t3.micro', 'AWS t3.nano', 'Azure B1s', 'GCP e2-micro', 'AWS t3.small']
    
    print("\n" + "="*60)
    print("TOPSIS RESULTS")
    print("="*60)
    
    # Sort by score
    ranking = np.argsort(scores)[::-1]
    
    for rank, idx in enumerate(ranking, 1):
        print(f"{rank}. {alternatives[idx]}: {scores[idx]:.6f}")
    
    print("="*60)
    print("✅ Test completed successfully!\n")


if __name__ == "__main__":
    test_topsis()
