import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', 'root'),
            'database': os.getenv('DB_NAME', 'cloud_recommendation_db')
        }
    
    def connect(self):
        """Create database connection"""
        return mysql.connector.connect(**self.config)
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute query and return results"""
        conn = None
        cursor = None
        try:
            conn = self.connect()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute(query, params or ())
            
            if query.strip().lower().startswith('select'):
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.lastrowid
            
            return result
        except Exception as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

db = Database()

def load_csv_to_database():
    """Load CSV data into MySQL database"""
    import pandas as pd
    import os
    
    try:
        # Create cloud_instance table
        create_table_query = """
            CREATE TABLE IF NOT EXISTS cloud_instance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                provider VARCHAR(50) NOT NULL,
                instance_type VARCHAR(100) NOT NULL,
                region VARCHAR(50) NOT NULL,
                vcpu INT NOT NULL,
                ram_gb DECIMAL(10,2) NOT NULL,
                storage_gb DECIMAL(10,2) NOT NULL,
                gpu INT DEFAULT 0,
                network_bandwidth VARCHAR(50),
                price_per_hour DECIMAL(10,6),
                security_score DECIMAL(5,2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_provider (provider),
                INDEX idx_region (region),
                INDEX idx_price (price_per_hour)
            )
        """
        db.execute_query(create_table_query, fetch=False)
        
        # Check if data already exists
        count_query = "SELECT COUNT(*) as count FROM cloud_instance"
        result = db.execute_query(count_query)
        if result and result[0]['count'] > 0:
            print(f"Database already has {result[0]['count']} instances")
            return
        
        # Load catalog data
        catalog_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'catalog_data.csv')
        if os.path.exists(catalog_path):
            df = pd.read_csv(catalog_path)
            print(f"Loading {len(df)} instances from catalog_data.csv")
            
            for _, row in df.iterrows():
                insert_query = """
                    INSERT INTO cloud_instance 
                    (provider, instance_type, region, vcpu, ram_gb, storage_gb, gpu, network_bandwidth, price_per_hour, security_score)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                # Extract price from catalog data if available
                price = 0.05  # Default price
                if 'price_per_hour' in row:
                    price = float(row['price_per_hour'])
                
                # Extract security score if available
                security = 75  # Default security
                if 'security_score' in row:
                    security = float(row['security_score'])
                
                db.execute_query(insert_query, (
                    row['provider'],
                    row['instance_type'],
                    row['region'],
                    int(row['vCPU']),
                    float(row['RAM_GB']),
                    float(row['storage_GB']),
                    int(row.get('GPU', 0)),
                    row.get('network_bandwidth', 'Standard'),
                    price,
                    security
                ), fetch=False)
            
            print(f"✓ Loaded {len(df)} instances into database")
        else:
            print("⚠️ catalog_data.csv not found")
            
    except Exception as e:
        print(f"Error loading CSV to database: {e}")