from database import db
import bcrypt
from datetime import datetime

class User:
    def __init__(self, id=None, username=None, email=None, password=None, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password = password
        self.created_at = created_at
    
    def create(self):
        hashed_password = bcrypt.hashpw(self.password.encode('utf-8'), bcrypt.gensalt())
        query = "INSERT INTO user (username, email, password_hash) VALUES (%s, %s, %s)"
        user_id = db.execute_query(query, (self.username, self.email, hashed_password.decode('utf-8')), fetch=False)
        return user_id
    
    @staticmethod
    def get_by_email(email):
        query = "SELECT * FROM user WHERE email = %s"
        result = db.execute_query(query, (email,))
        if result:
            user_data = result[0]
            return User(id=user_data['id'], username=user_data['username'], 
                       email=user_data['email'], password=user_data['password_hash'])
        return None
    
    @staticmethod
    def get_by_id(user_id):
        query = "SELECT * FROM user WHERE id = %s"
        result = db.execute_query(query, (user_id,))
        if result:
            user_data = result[0]
            return User(id=user_data['id'], username=user_data['username'], 
                       email=user_data['email'], password=user_data['password_hash'])
        return None
    
    def verify_password(self, password):
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
        except Exception:
            return False

class Review:
    def __init__(self, id=None, user_id=None, username=None, selected_provider=None, 
                 selected_instance=None, topsis_score=None, rating=None, 
                 review_text=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.username = username
        self.selected_provider = selected_provider
        self.selected_instance = selected_instance
        self.topsis_score = topsis_score
        self.rating = rating
        self.review_text = review_text
        self.created_at = created_at
    
    def create(self):
        # First create a recommendation record
        rec_query = """INSERT INTO recommendation 
                       (user_id, provider, instance_type, region, price_per_hour, vcpu, ram_gb, storage_gb, security_score, topsis_score) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        rec_id = db.execute_query(rec_query, (
            self.user_id, 
            self.selected_provider or 'Unknown',
            self.selected_instance or 'Unknown', 
            'us-east-1', 0.1, 2, 4, 100, 75, 
            self.topsis_score or 0.5
        ), fetch=False)
        
        if rec_id:
            query = """INSERT INTO rating 
                       (user_id, recommendation_id, rating, comment) 
                       VALUES (%s, %s, %s, %s)"""
            return db.execute_query(query, (self.user_id, rec_id, self.rating, self.review_text), fetch=False)
        return None
    
    @staticmethod
    def get_all():
        query = """SELECT r.rating, r.comment, u.username, 
                   COALESCE(rec.provider, 'Unknown') as provider,
                   COALESCE(rec.instance_type, 'Unknown') as instance_type,
                   COALESCE(rec.topsis_score, 0) as topsis_score,
                   r.created_at
                   FROM rating r 
                   JOIN user u ON r.user_id = u.id 
                   LEFT JOIN recommendation rec ON r.recommendation_id = rec.id
                   ORDER BY r.created_at DESC 
                   LIMIT 50"""
        result = db.execute_query(query)
        if result:
            # Format the data properly for frontend
            formatted_reviews = []
            for row in result:
                formatted_reviews.append({
                    'username': row['username'],
                    'provider': row['provider'],
                    'instance_type': row['instance_type'], 
                    'rating': int(row['rating']) if row['rating'] else 0,
                    'comment': row['comment'] or '',
                    'topsis_score': float(row['topsis_score']) if row['topsis_score'] else 0.0,
                    'created_at': row['created_at']
                })
            return formatted_reviews
        return []
    
    @staticmethod
    def get_by_user(user_id):
        query = "SELECT * FROM rating WHERE user_id = %s ORDER BY created_at DESC"
        return db.execute_query(query, (user_id,))
    
    @staticmethod
    def get_happy_users_count():
        """Get count of unique users who gave rating >= 4"""
        query = "SELECT COUNT(DISTINCT user_id) as count FROM rating WHERE rating >= 4"
        result = db.execute_query(query)
        if result and len(result) > 0:
            return int(result[0]['count'])
        return 0
    
    @staticmethod
    def get_total_count():
        """Get total count of all recommendations/ratings"""
        query = "SELECT COUNT(*) as count FROM recommendation"
        result = db.execute_query(query)
        if result and len(result) > 0:
            return int(result[0]['count'])
        return 0

class UserRating:
    def __init__(self, id=None, user_id=None, instance_id=None, rating=None, comment=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.instance_id = instance_id
        self.rating = rating
        self.comment = comment
        self.created_at = created_at
    
    def create_or_update(self):
        # Check if rating exists
        check_query = "SELECT id FROM rating WHERE user_id = %s AND recommendation_id = %s"
        existing = db.execute_query(check_query, (self.user_id, self.instance_id))
        
        if existing:
            if self.comment is not None:
                query = "UPDATE rating SET rating = %s, comment = %s WHERE user_id = %s AND recommendation_id = %s"
                return db.execute_query(query, (self.rating, self.comment, self.user_id, self.instance_id), fetch=False)
            query = "UPDATE rating SET rating = %s WHERE user_id = %s AND recommendation_id = %s"
            return db.execute_query(query, (self.rating, self.user_id, self.instance_id), fetch=False)
        else:
            query = "INSERT INTO rating (user_id, recommendation_id, rating, comment) VALUES (%s, %s, %s, %s)"
            return db.execute_query(query, (self.user_id, self.instance_id, self.rating, self.comment), fetch=False)
    
    @staticmethod
    def get_user_ratings(user_id):
        query = "SELECT * FROM rating WHERE user_id = %s"
        return db.execute_query(query, (user_id,))
    
    @staticmethod
    def get_avg_rating_by_instance(provider, instance_type):
        """Get average rating for a specific instance"""
        query = """SELECT AVG(r.rating) as avg_rating, COUNT(r.rating) as rating_count
                   FROM rating r
                   JOIN recommendation rec ON r.recommendation_id = rec.id
                   WHERE rec.provider = %s AND rec.instance_type = %s"""
        result = db.execute_query(query, (provider, instance_type))
        if result and result[0]['avg_rating']:
            return float(result[0]['avg_rating']), int(result[0]['rating_count'])
        return 0.0, 0
    
    @staticmethod
    def check_user_rated(user_id, provider, instance_type):
        """Check if user already rated this instance"""
        query = """SELECT r.rating FROM rating r
                   JOIN recommendation rec ON r.recommendation_id = rec.id
                   WHERE r.user_id = %s AND rec.provider = %s AND rec.instance_type = %s
                   LIMIT 1"""
        result = db.execute_query(query, (user_id, provider, instance_type))
        if result:
            return int(result[0]['rating'])
        return None