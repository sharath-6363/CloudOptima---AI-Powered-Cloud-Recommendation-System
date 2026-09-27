from flask import Flask, request, jsonify
from flask_cors import CORS
from auth import generate_token, token_required
from models import User, Review, UserRating
import numpy as np
from datetime import datetime
import traceback
import sys
import os
import pandas as pd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import components with enhanced error handling
try:
    from src.data_loader import DataLoader
    print("✅ DataLoader imported successfully")
except ImportError as e:
    print(f"❌ DataLoader import error: {e}")
    DataLoader = None

try:
    from src.topsis import TOPSIS
    print("✅ TOPSIS imported successfully")
except ImportError as e:
    print(f"❌ TOPSIS import error: {e}")
    TOPSIS = None

try:
    from src.llm_module import LLMRecommender
    print("✅ LLMRecommender imported successfully")
except ImportError as e:
    print(f"❌ LLMRecommender import error: {e}. LLM features will be disabled.")
    LLMRecommender = None

try:
    from src.enhanced_topsis import EnhancedTOPSIS
    print("✅ EnhancedTOPSIS imported successfully")
except ImportError as e:
    print(f"❌ EnhancedTOPSIS import error: {e}. Using standard TOPSIS.")
    EnhancedTOPSIS = None

try:
    from src.ml_predictor import MLPredictor
    print("✅ MLPredictor imported successfully")
except ImportError as e:
    print(f"❌ MLPredictor import error: {e}. ML features will be disabled.")
    MLPredictor = None

app = Flask(__name__)

# Configure CORS - Allow all origins for development
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Credentials"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True
)

# Add explicit OPTIONS handler for preflight requests
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

# Initialize components with individual error handling
components_loaded = True
data_loader = None
topsis = None
llm_recommender = None
enhanced_topsis = None
ml_predictor = None

if DataLoader:
    try:
        data_loader = DataLoader(data_dir="data")
        print("✅ DataLoader initialized")
    except Exception as e:
        print(f"❌ DataLoader initialization error: {e}")
        components_loaded = False
else:
    components_loaded = False

if TOPSIS:
    try:
        topsis = TOPSIS()
        print("✅ TOPSIS initialized")
    except Exception as e:
        print(f"❌ TOPSIS initialization error: {e}")
        components_loaded = False
else:
    components_loaded = False

if LLMRecommender:
    try:
        llm_recommender = LLMRecommender()
        print("✅ LLMRecommender initialized")
    except Exception as e:
        print(f"❌ LLMRecommender initialization error: {e}")
        print("   Creating fallback LLM instance...")
        # Don't set to None - the error is in __init__, create anyway
        try:
            llm_recommender = LLMRecommender()
        except:
            llm_recommender = None
else:
    llm_recommender = None

if EnhancedTOPSIS:
    try:
        enhanced_topsis = EnhancedTOPSIS()
        print("✅ EnhancedTOPSIS initialized")
    except Exception as e:
        print(f"⚠️ EnhancedTOPSIS initialization error: {e}")
        enhanced_topsis = None

if MLPredictor:
    try:
        ml_predictor = MLPredictor()
        print("✅ MLPredictor initialized")
    except Exception as e:
        print(f"⚠️ MLPredictor initialization error: {e}")
        ml_predictor = None
else:
    ml_predictor = None

print(f"📦 Core components loaded: {components_loaded}")

# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@app.route('/api/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.json
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not all([username, email, password]):
            return jsonify({'message': 'All fields are required'}), 400

        # Check if user exists
        existing_user = User.get_by_email(email)
        if existing_user:
            return jsonify({'message': 'User already exists'}), 400

        # Create new user
        user = User(username=username, email=email, password=password)
        user_id = user.create()

        if user_id:
            token = generate_token(user_id)
            return jsonify({
                'message': 'User created successfully',
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email
                }
            }), 201
        else:
            return jsonify({'message': 'Failed to create user'}), 500

    except Exception as e:
        print(f"❌ Registration error: {str(e)}")
        return jsonify({'message': f'Registration error: {str(e)}'}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'message': 'Email and password are required'}), 400

        user = User.get_by_email(email)
        if user and user.verify_password(password):
            token = generate_token(user.id)
            return jsonify({
                'message': 'Login successful',
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                }
            }), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'message': f'Login error: {str(e)}'}), 500


# ============================================================================
# RECOMMENDATION ROUTE (FIXED)
# ============================================================================

@app.route('/api/recommend', methods=['POST'])
@app.route('/api/recommendations', methods=['POST'])
@token_required
def get_recommendations(user_id):
    """
    FIXED: Get cloud instance recommendations using TOPSIS on real dataset
    - Loads 3000 rows from CSV files (NO sample/dummy data)
    - Validates dataset and region
    - Returns proper error messages
    """
    try:
        # Check if core components are loaded
        if not components_loaded or not data_loader or not topsis:
            return jsonify({
                'error': 'SYSTEM_ERROR',
                'message': 'System components not available. Please check server configuration.'
            }), 503

        # Parse request data
        data = request.json
        budget = float(data.get('budget', 0.2))
        region = data.get('region')
        # Clean region - remove any extra text/numbers
        if region:
            region = region.split()[0]  # Take only first part before space
        weights = data.get('weights', [0.2, 0.2, 0.2, 0.2, 0.2])

        # Validate inputs
        if not region:
            return jsonify({
                'error': 'INVALID_INPUT',
                'message': 'Region parameter is required'
            }), 400

        if budget <= 0:
            return jsonify({
                'error': 'INVALID_INPUT',
                'message': 'Budget must be greater than 0'
            }), 400

        print(f"\n{'='*60}")
        print(f"🔍 NEW RECOMMENDATION REQUEST")
        print(f"{'='*60}")
        print(f"   User ID: {user_id}")
        print(f"   Budget: ${budget:.4f}/hour")
        print(f"   Region: {region}")
        print(f"   Weights: {weights}")

        # STEP 1: Load data from CSV files (NOT sample data)
        print(f"\n📂 STEP 1: Loading data from CSV files...")
        try:
            full_data = data_loader.load_all_data()
        except FileNotFoundError as e:
            print(f"❌ CSV files not found: {e}")
            return jsonify({
                'error': 'NO_DATA_FETCHED',
                'message': f'Dataset files not found: {str(e)}'
            }), 500
        except ValueError as e:
            error_str = str(e)
            if "INSUFFICIENT_DATA" in error_str:
                print(f"❌ Insufficient data: {e}")
                return jsonify({
                    'error': 'INSUFFICIENT_DATA',
                    'message': error_str
                }), 500
            elif "NO_DATA_FETCHED" in error_str:
                print(f"❌ No data fetched: {e}")
                return jsonify({
                    'error': 'NO_DATA_FETCHED',
                    'message': 'No valid data fetched from dataset'
                }), 500
            else:
                raise
        except Exception as e:
            print(f"❌ Data loading error: {e}")
            return jsonify({
                'error': 'SYSTEM_ERROR',
                'message': f'Error loading dataset: {str(e)}'
            }), 500

        print(f"✅ Loaded {len(full_data)} rows from CSV dataset")

        # STEP 2: Validate dataset size
        if len(full_data) < 3000:
            print(f"❌ Dataset has only {len(full_data)} rows (expected 3000)")
            return jsonify({
                'error': 'INSUFFICIENT_DATA',
                'message': f'Expected 3000 rows but found {len(full_data)}'
            }), 500

        print(f"✅ Dataset validation passed: {len(full_data)} rows")
        print(f"   Available regions: {len(full_data['region'].unique())} unique regions")
        print(f"   Price range: ${full_data['price_per_hour'].min():.4f} - ${full_data['price_per_hour'].max():.4f}/hour")

        # STEP 3: Filter data by region and budget
        print(f"\n🎯 STEP 2: Filtering data (region={region}, budget=${budget})...")
        try:
            filtered_data = data_loader.filter_data(full_data, region, budget)
        except ValueError as e:
            # Region not found or no data in budget
            print(f"❌ Filter error: {e}")
            return jsonify({
                'error': 'NO_DATA_FETCHED',
                'message': str(e)
            }), 404

        if len(filtered_data) == 0:
            print(f"❌ No instances found after filtering")
            return jsonify({
                'error': 'NO_DATA_FETCHED',
                'message': f'No valid rows in dataset for region={region}, budget=${budget}'
            }), 404

        print(f"✅ Filtered to {len(filtered_data)} instances")
        print(f"   Price range: ${filtered_data['price_per_hour'].min():.4f} - ${filtered_data['price_per_hour'].max():.4f}/hour")

        # STEP 4: Prepare decision matrix for TOPSIS
        print(f"\n📊 STEP 3: Preparing TOPSIS decision matrix...")
        try:
            decision_matrix, instance_info = data_loader.prepare_decision_matrix(filtered_data)
        except ValueError as e:
            print(f"❌ Matrix preparation error: {e}")
            return jsonify({
                'error': 'SYSTEM_ERROR',
                'message': f'Error preparing decision matrix: {str(e)}'
            }), 500

        print(f"✅ Decision matrix prepared: {decision_matrix.shape}")
        print(f"   Criteria count: {decision_matrix.shape[1]}")
        print(f"   Alternatives count: {decision_matrix.shape[0]}")

        # STEP 5: Configure TOPSIS criteria
        # Criteria order matches decision matrix columns:
        # ['price_per_hour', 'performance', 'security_score', 'availability', 'bandwidth_score', 'latency', 'cost_per_vcpu']
        criteria_types = ['cost', 'benefit', 'benefit', 'benefit', 'benefit', 'cost', 'cost']
        
        # Normalize user weights
        raw_weights = np.array(weights, dtype=float)
        num_criteria = decision_matrix.shape[1]
        
        if len(raw_weights) < num_criteria:
            # Pad with equal weights if not enough provided
            padding = np.full(num_criteria - len(raw_weights), 1.0/num_criteria)
            raw_weights = np.concatenate([raw_weights, padding])
        elif len(raw_weights) > num_criteria:
            raw_weights = raw_weights[:num_criteria]
        
        # Normalize to sum to 1
        normalized_weights = raw_weights / raw_weights.sum()
        
        print(f"\n⚖️ STEP 4: Configuring TOPSIS...")
        print(f"   Criteria types: {criteria_types}")
        print(f"   User weights: {weights}")
        print(f"   Normalized weights: {normalized_weights.tolist()}")

        # STEP 6: Run TOPSIS
        print(f"\n🔬 STEP 5: Running TOPSIS analysis...")
        try:
            topsis_scores = topsis.run_topsis(decision_matrix, normalized_weights, criteria_types)
        except Exception as e:
            print(f"❌ TOPSIS computation error: {e}")
            return jsonify({
                'error': 'SYSTEM_ERROR',
                'message': f'Error computing TOPSIS scores: {str(e)}'
            }), 500

        print(f"✅ TOPSIS scores computed")
        print(f"   Score range: {topsis_scores.min():.4f} - {topsis_scores.max():.4f}")

        # STEP 7: Add scores and rank results
        results_df = instance_info.copy()
        results_df['topsis_score'] = topsis_scores
        
        # Sort by score (descending)
        results_df = results_df.sort_values('topsis_score', ascending=False).reset_index(drop=True)
        
        # Get top 5 recommendations
        top_k = min(5, len(results_df))
        top_options = results_df.head(top_k)
        
        print(f"\n🏆 STEP 6: Top {top_k} recommendations selected")
        for i in range(min(5, len(top_options))):
            row = top_options.iloc[i]
            print(f"   #{i+1}: {row['provider']} {row['instance_type']} - ${row['price_per_hour']:.4f}/hour (TOPSIS: {row['topsis_score']:.6f})")

        # STEP 8: Format recommendations for JSON response
        recommendations = []
        for position, (idx, row) in enumerate(top_options.iterrows()):
            provider = str(row['provider'])
            instance_type = str(row['instance_type'])
            avg_rating, rating_count = UserRating.get_avg_rating_by_instance(provider, instance_type)
            user_rating = UserRating.check_user_rated(user_id, provider, instance_type)
            
            rec = {
                'rank': position + 1,
                'provider': provider,
                'instance_type': instance_type,
                'region': str(row['region']),
                'price_per_hour': float(row['price_per_hour']),
                'vCPU': int(row['vCPU']),
                'RAM_GB': float(row['RAM_GB']),
                'storage_GB': float(row['storage_GB']),
                'security_score': float(row['security_score']),
                'performance': float(row['performance']),
                'availability': float(row['availability']),
                'latency': float(row['latency']),
                'bandwidth_score': float(row['bandwidth_score']),
                'topsis_score': float(row['topsis_score']),
                'network_bandwidth': str(row.get('network_bandwidth', 'Unknown')),
                'GPU': int(row.get('GPU', 0)),
                'risk_score': 1.0 - float(row['topsis_score']),
                'avg_rating': avg_rating,
                'rating_count': rating_count,
                'user_rating': user_rating,
                'user_has_rated': user_rating is not None  # Flag to prevent duplicate ratings
            }
            rec['ml_satisfaction_score'] = float(row['topsis_score'])
            rec['hybrid_score'] = float(row['topsis_score'])
            recommendations.append(rec)

        # STEP 9: Enhance with ML predictions (IF MODEL IS LOADED)
        # ML adds hybrid scores and may re-rank based on learned patterns
        if ml_predictor and ml_predictor.is_loaded:
            print(f"\n🤖 STEP 8: Enhancing recommendations with ML predictions...")
            try:
                recommendations = ml_predictor.enhance_recommendations(recommendations)
                
                # STEP 8.5: Add rating boost to hybrid scores
                print(f"\n⭐ Adding user rating boost to recommendations...")
                for rec in recommendations:
                    # Rating boost: 0-10% based on average rating (0-5 stars)
                    # Formula: rating_boost = (avg_rating / 5.0) * 0.10
                    # High ratings (5 stars) = +10%, Low ratings (1 star) = +2%
                    if rec['avg_rating'] > 0 and rec['rating_count'] >= 3:
                        # Only apply boost if at least 3 users rated it (reliability threshold)
                        rating_boost = (rec['avg_rating'] / 5.0) * 0.10
                        rec['hybrid_score'] = rec['hybrid_score'] * (1 + rating_boost)
                        print(f"   {rec['provider']} {rec['instance_type']}: Rating {rec['avg_rating']:.1f}/5 ({rec['rating_count']} users) → +{rating_boost*100:.1f}% boost")
                
                # Re-sort by hybrid score (now includes rating boost)
                recommendations.sort(key=lambda x: x['hybrid_score'], reverse=True)
                # Update ranks after re-sorting
                for i, rec in enumerate(recommendations):
                    rec['rank'] = i + 1
                print(f"✅ ML enhancement completed and re-ranked by hybrid scores (with rating boost)")
                print(f"🔍 Final ranking after ML + Rating boost:")
                for i in range(min(3, len(recommendations))):
                    rec = recommendations[i]
                    print(f"   #{i+1}: {rec['provider']} {rec['instance_type']} (Hybrid: {rec['hybrid_score']:.6f}, Rating: {rec['avg_rating']:.1f}/5)")
            except Exception as e:
                print(f"⚠️ ML enhancement failed: {e}")
        else:
            print(f"\n⚠️ STEP 8: ML model not loaded, using TOPSIS-only ranking")
            # Even without ML, apply rating boost to TOPSIS scores
            print(f"\n⭐ Adding user rating boost to TOPSIS scores...")
            for rec in recommendations:
                if rec['avg_rating'] > 0 and rec['rating_count'] >= 3:
                    rating_boost = (rec['avg_rating'] / 5.0) * 0.10
                    rec['hybrid_score'] = rec['hybrid_score'] * (1 + rating_boost)
            recommendations.sort(key=lambda x: x['hybrid_score'], reverse=True)
            for i, rec in enumerate(recommendations):
                rec['rank'] = i + 1
        
        # STEP 10: Generate AI explanation AFTER ML enhancement (ALWAYS generate detailed explanation)
        # This ensures the LLM explains the ACTUAL #1 recommendation shown to the user
        print(f"\n🤖 STEP 9: Generating AI explanation for final ranked recommendations...")
        explanation = None
        if llm_recommender:
            try:
                user_prefs = {
                    'budget': float(budget),
                    'region': region,
                    'weights': normalized_weights.tolist(),
                    'raw_weights': raw_weights.tolist()
                }
                
                # Convert recommendations list to DataFrame for LLM
                final_recs_df = pd.DataFrame(recommendations)
                
                full_dataset_stats = data_loader.get_dataset_statistics(full_data)
                prompt = llm_recommender.build_prompt(user_prefs, final_recs_df, full_dataset_stats)
                explanation = llm_recommender.get_explanation(prompt)
                print(f"✅ AI explanation generated ({len(explanation)} chars)")
            except Exception as e:
                print(f"⚠️ LLM explanation failed: {e}")
                traceback.print_exc()
                explanation = f"Based on hybrid analysis of {len(filtered_data)} instances in {region} region with budget ${budget}/hour."
        else:
            print(f"⚠️ LLM not available - using simple fallback")
            explanation = f"Based on hybrid analysis of {len(filtered_data)} instances in {region} region with budget ${budget}/hour."
        
        print(f"\n✅ SUCCESS: Returning {len(recommendations)} recommendations")
        print(f"{'='*60}\n")

        return jsonify({
            'recommendations': recommendations,
            'ai_explanation': explanation,
            'best_option': recommendations[0] if recommendations else None,
            'total_analyzed': len(filtered_data),
            'dataset_size': len(full_data),
            'ml_enabled': ml_predictor.is_loaded if ml_predictor else False,
            'request_params': {
                'region': region,
                'budget': budget,
                'weights': weights
            }
        }), 200

    except Exception as e:
        print(f"\n{'='*60}")
        print(f"❌ CRITICAL ERROR")
        print(f"{'='*60}")
        print(f"Error: {str(e)}")
        print(f"Traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")
        
        return jsonify({
            'error': 'SYSTEM_ERROR',
            'message': f'Error generating recommendations: {str(e)}',
            'recommendations': [],
            'total_analyzed': 0
        }), 500


# ============================================================================
# REVIEW ROUTES
# ============================================================================

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Get all reviews"""
    try:
        reviews = Review.get_all()
        return jsonify({'reviews': reviews}), 200
    except Exception as e:
        print(f"❌ Error fetching reviews: {str(e)}")
        return jsonify({'message': f'Error fetching reviews: {str(e)}'}), 500


@app.route('/api/reviews', methods=['POST'])
@token_required
def create_review(user_id):
    """Create a new review"""
    try:
        data = request.json
        selected_provider = data.get('selected_provider')
        selected_instance = data.get('selected_instance')
        topsis_score = data.get('topsis_score')
        rating = data.get('rating')
        review_text = data.get('review_text', '')

        user = User.get_by_id(user_id)
        if not user:
            return jsonify({'message': 'User not found'}), 404

        review = Review(
            user_id=user_id,
            username=user.username,
            selected_provider=selected_provider,
            selected_instance=selected_instance,
            topsis_score=topsis_score,
            rating=rating,
            review_text=review_text
        )

        review_id = review.create()
        if review_id:
            return jsonify({'message': 'Review submitted successfully'}), 201
        else:
            return jsonify({'message': 'Failed to submit review'}), 500

    except Exception as e:
        print(f"❌ Error creating review: {str(e)}")
        return jsonify({'message': f'Error creating review: {str(e)}'}), 500


# ============================================================================
# RATING ROUTES
# ============================================================================

@app.route('/api/ratings', methods=['POST'])
@token_required
def submit_rating(user_id):
    """Submit a rating (only once per instance per user)"""
    try:
        data = request.json
        provider = data.get('provider')
        instance_type = data.get('instance_type')
        rating = data.get('rating')
        comment = data.get('comment', '')

        # Recommendation fields needed to satisfy DB NOT NULL constraints
        region = data.get('region')
        price_per_hour = data.get('price_per_hour')
        vcpu = data.get('vCPU')
        ram_gb = data.get('RAM_GB')
        storage_gb = data.get('storage_GB')
        security_score = data.get('security_score')
        topsis_score = data.get('topsis_score')

        if not provider or not instance_type:
            return jsonify({'error': 'provider and instance_type are required'}), 400
        
        # Validate rating value
        try:
            rating = int(rating)
        except Exception:
            return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

        if rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400

        # Validate required recommendation fields (avoid DB 500s)
        required_fields = {
            'region': region,
            'price_per_hour': price_per_hour,
            'vCPU': vcpu,
            'RAM_GB': ram_gb,
            'storage_GB': storage_gb,
            'security_score': security_score,
            'topsis_score': topsis_score,
        }
        missing = [k for k, v in required_fields.items() if v is None or v == '']
        if missing:
            return jsonify({
                'error': 'MISSING_FIELDS',
                'message': f"Missing required fields: {', '.join(missing)}",
            }), 400
        
        # CHECK: Prevent duplicate ratings
        existing_rating = UserRating.check_user_rated(user_id, provider, instance_type)
        if existing_rating is not None:
            return jsonify({
                'error': 'ALREADY_RATED',
                'message': f'You already rated this instance with {existing_rating} stars. You cannot rate it again.',
                'existing_rating': existing_rating
            }), 409  # 409 Conflict

        from database import db

        # Create a recommendation record with required fields (schema has NOT NULL columns)
        try:
            rec_query = """INSERT INTO recommendation 
                           (user_id, provider, instance_type, region, price_per_hour, vcpu, ram_gb, storage_gb, security_score, topsis_score)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            rec_id = db.execute_query(
                rec_query,
                (
                    user_id,
                    str(provider),
                    str(instance_type),
                    str(region),
                    float(price_per_hour),
                    int(vcpu),
                    int(round(float(ram_gb))),
                    int(round(float(storage_gb))),
                    int(round(float(security_score))),
                    float(topsis_score),
                ),
                fetch=False,
            )
        except Exception as e:
            return jsonify({'error': f'Invalid recommendation fields: {str(e)}'}), 400

        if not rec_id:
            return jsonify({'error': 'Failed to create recommendation record'}), 500
        
        # Submit rating
        user_rating = UserRating(
            user_id=user_id,
            instance_id=rec_id,
            rating=rating,
            comment=comment
        )
        
        result = user_rating.create_or_update()
        if result:
            return jsonify({
                'message': '✅ Rating submitted successfully',
                'rating': rating,
                'feedback': 'Thank you for your feedback!'
            }), 201
        else:
            return jsonify({'error': 'Failed to submit rating'}), 500

    except Exception as e:
        print(f"❌ Error submitting rating: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error submitting rating: {str(e)}'}), 500


@app.route('/api/user/ratings', methods=['GET'])
@token_required
def get_user_ratings(user_id):
    """Get all ratings for a user"""
    try:
        ratings = UserRating.get_user_ratings(user_id)
        return jsonify({'ratings': ratings}), 200
    except Exception as e:
        print(f"❌ Error fetching ratings: {str(e)}")
        return jsonify({'message': f'Error fetching ratings: {str(e)}'}), 500


# ============================================================================
# DATA INFO ROUTES
# ============================================================================

@app.route('/api/regions', methods=['GET'])
def get_regions():
    """Get list of available regions from dataset"""
    try:
        if not components_loaded or not data_loader:
            return jsonify({
                'error': 'SYSTEM_ERROR',
                'regions': []
            }), 503

        full_data = data_loader.load_all_data()
        
        if len(full_data) == 0:
            return jsonify({'regions': []}), 200

        regions = sorted(full_data['region'].unique())
        region_options = [{'value': region, 'label': region} for region in regions]

        return jsonify({'regions': region_options}), 200

    except Exception as e:
        print(f"❌ Error fetching regions: {str(e)}")
        return jsonify({
            'message': f'Error fetching regions: {str(e)}',
            'regions': []
        }), 500


@app.route('/api/dataset-info', methods=['GET'])
def get_dataset_info():
    """Get comprehensive dataset statistics"""
    try:
        if not components_loaded or not data_loader:
            return jsonify({
                'error': 'SYSTEM_ERROR',
                'message': 'Data loader not available',
                'total_instances': 0,
                'providers': [],
                'regions': []
            }), 503

        full_data = data_loader.load_all_data()

        if len(full_data) == 0:
            return jsonify({
                'total_instances': 0,
                'providers': [],
                'regions': [],
                'provider_counts': {},
                'dataset_info': {'total_instances': 0}
            }), 200

        stats = data_loader.get_dataset_statistics(full_data)

        # Provider counts
        provider_counts = {}
        if 'provider' in full_data.columns:
            provider_counts = full_data['provider'].value_counts().to_dict()

        return jsonify({
            'total_instances': len(full_data),
            'providers': stats.get('providers', []),
            'regions': stats.get('regions', []),
            'provider_counts': provider_counts,
            'dataset_info': stats
        }), 200

    except Exception as e:
        print(f"❌ Error fetching dataset info: {str(e)}")
        return jsonify({
            'message': f'Error fetching dataset info: {str(e)}',
            'total_instances': 0
        }), 500


@app.route('/api/debug-data', methods=['GET'])
def debug_data():
    """Debug endpoint to inspect loaded data"""
    try:
        if not components_loaded or not data_loader:
            return jsonify({'error': 'Components not loaded'}), 503

        full_data = data_loader.load_all_data()

        debug_info = {
            'total_rows': len(full_data),
            'columns': list(full_data.columns) if len(full_data) > 0 else [],
            'sample_data': full_data.head(5).to_dict('records') if len(full_data) > 0 else [],
            'regions': list(full_data['region'].unique()) if len(full_data) > 0 and 'region' in full_data.columns else [],
            'providers': list(full_data['provider'].unique()) if len(full_data) > 0 and 'provider' in full_data.columns else [],
            'price_range': {
                'min': float(full_data['price_per_hour'].min()) if len(full_data) > 0 and 'price_per_hour' in full_data.columns else 0,
                'max': float(full_data['price_per_hour'].max()) if len(full_data) > 0 and 'price_per_hour' in full_data.columns else 0
            }
        }

        return jsonify(debug_info), 200

    except Exception as e:
        print(f"❌ Debug error: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Debug error: {str(e)}'}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get real statistics from database and dataset"""
    try:
        # Get happy users count (users with rating >= 4)
        happy_users = Review.get_happy_users_count()
        
        # Get total recommendations count
        total_recommendations = Review.get_total_count()
        
        # Get unique providers count from dataset
        providers_count = 11  # Default
        if components_loaded and data_loader:
            try:
                full_data = data_loader.load_all_data()
                if len(full_data) > 0 and 'provider' in full_data.columns:
                    providers_count = len(full_data['provider'].unique())
            except:
                pass
        
        return jsonify({
            'stats': {
                'users': happy_users,
                'recommendations': total_recommendations,
                'providers': providers_count
            }
        }), 200
    except Exception as e:
        print(f"❌ Error fetching stats: {str(e)}")
        return jsonify({
            'stats': {
                'users': 0,
                'recommendations': 0,
                'providers': 11
            }
        }), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'components_loaded': components_loaded,
        'data_loader_available': data_loader is not None,
        'topsis_available': topsis is not None,
        'llm_available': llm_recommender is not None,
        'timestamp': datetime.now().isoformat()
    }), 200


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 CLOUD RECOMMENDATION API SERVER")
    print("="*60)
    print(f"📦 Components loaded: {components_loaded}")
    print(f"   DataLoader: {'✅' if data_loader else '❌'}")
    print(f"   TOPSIS: {'✅' if topsis else '❌'}")
    print(f"   LLM: {'✅' if llm_recommender else '⚠️ (optional)'}")
    print(f"   Enhanced TOPSIS: {'✅' if enhanced_topsis else '⚠️ (optional)'}")
    
    if components_loaded and data_loader:
        print(f"\n📊 Testing data loading...")
        try:
            test_data = data_loader.load_all_data()
            print(f"✅ Data loaded successfully: {len(test_data)} instances")
            
            if len(test_data) > 0:
                print(f"   Providers: {', '.join(test_data['provider'].unique())}")
                print(f"   Regions: {len(test_data['region'].unique())} unique regions")
                print(f"   Price range: ${test_data['price_per_hour'].min():.4f} - ${test_data['price_per_hour'].max():.4f}/hour")
                
                # Show sample regions
                sample_regions = sorted(test_data['region'].unique())[:5]
                print(f"   Sample regions: {', '.join(sample_regions)}")
                
            else:
                print(f"⚠️ WARNING: No data loaded from CSV files")
                
        except Exception as e:
            print(f"❌ Data loading test failed: {e}")
            traceback.print_exc()
    else:
        print(f"\n⚠️ WARNING: Core components not loaded. Server will return errors.")
    
    print(f"\n🌐 Starting Flask server on http://0.0.0.0:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')
