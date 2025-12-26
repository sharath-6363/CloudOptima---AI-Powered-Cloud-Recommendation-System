import pandas as pd
import numpy as np
from pathlib import Path
import os

class DataLoader:
    def __init__(self, data_dir="data"):
        """Initialize DataLoader with path to CSV files"""
        self.data_dir = Path(data_dir)
        print(f"📂 DataLoader initialized with data directory: {self.data_dir}")
        
        # Verify CSV files exist
        self.catalog_file = self.data_dir / "catalog_data.csv"
        self.cost_file = self.data_dir / "cost_data.csv"
        self.security_file = self.data_dir / "security_data.csv"
        
        files_exist = all([
            self.catalog_file.exists(),
            self.cost_file.exists(),
            self.security_file.exists()
        ])
        
        if not files_exist:
            raise FileNotFoundError(
                f"Required CSV files not found in {self.data_dir}. "
                f"Expected: catalog_data.csv, cost_data.csv, security_data.csv"
            )
        
        print(f"✅ All required CSV files found")

    def load_all_data(self):
        """Load and merge all datasets from CSV files - NO FALLBACK DATA"""
        try:
            print("📂 Loading data from CSV files...")
            
            # Load the three CSV files
            catalog_df = pd.read_csv(self.catalog_file)
            cost_df = pd.read_csv(self.cost_file)
            security_df = pd.read_csv(self.security_file)
            
            print(f"✅ Loaded catalog_data.csv: {len(catalog_df)} rows")
            print(f"✅ Loaded cost_data.csv: {len(cost_df)} rows")
            print(f"✅ Loaded security_data.csv: {len(security_df)} rows")
            
            # Validate row counts
            if len(catalog_df) < 3000:
                raise ValueError(f"INSUFFICIENT_DATA: Expected 3000 rows but found {len(catalog_df)} in catalog_data.csv")
            
            # Validate required columns
            required_catalog_cols = ['provider', 'instance_type', 'region', 'vCPU', 'RAM_GB', 'storage_GB', 'network_bandwidth']
            required_cost_cols = ['provider', 'instance_type', 'region', 'price_per_hour']
            required_security_cols = ['provider', 'region', 'security_score']
            
            missing_catalog = [col for col in required_catalog_cols if col not in catalog_df.columns]
            missing_cost = [col for col in required_cost_cols if col not in cost_df.columns]
            missing_security = [col for col in required_security_cols if col not in security_df.columns]
            
            if missing_catalog or missing_cost or missing_security:
                raise ValueError(
                    f"Missing required columns - "
                    f"Catalog: {missing_catalog}, Cost: {missing_cost}, Security: {missing_security}"
                )
            
            # Merge datasets
            print("🔗 Merging datasets...")
            
            # Step 1: Merge catalog with cost data
            merged_df = catalog_df.merge(
                cost_df[['provider', 'instance_type', 'region', 'price_per_hour']],
                on=['provider', 'instance_type', 'region'],
                how='left'
            )
            
            # Step 2: Merge with security data
            merged_df = merged_df.merge(
                security_df[['provider', 'region', 'security_score']],
                on=['provider', 'region'],
                how='left'
            )
            
            print(f"✅ Merged dataset: {len(merged_df)} rows")
            
            # Check for valid rows after merge
            valid_rows = merged_df.dropna(subset=['price_per_hour', 'security_score'])
            if len(valid_rows) == 0:
                raise ValueError("NO_DATA_FETCHED: No valid rows after merging datasets")
            
            # Process network bandwidth to numeric
            self._process_network_bandwidth(merged_df)
            
            # Add derived metrics required for TOPSIS
            self._add_derived_metrics(merged_df)
            
            # Validate final required columns for TOPSIS
            final_required_cols = ['provider', 'region', 'price', 'performance', 'security_score', 
                                   'latency', 'availability', 'bandwidth', 'cost']
            
            # Map existing columns to required names
            merged_df['price'] = merged_df['price_per_hour']
            merged_df['cost'] = merged_df['price_per_hour']  # cost is same as price
            merged_df['bandwidth'] = merged_df['bandwidth_score']  # from network processing
            
            print(f"✅ Dataset ready: {len(merged_df)} rows with {len(merged_df.columns)} columns")
            print(f"   Providers: {merged_df['provider'].unique().tolist()}")
            print(f"   Regions: {len(merged_df['region'].unique())} unique regions")
            print(f"   Price range: ${merged_df['price_per_hour'].min():.4f} - ${merged_df['price_per_hour'].max():.4f}/hour")
            
            return merged_df
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"CSV file not found: {e}")
        except ValueError as e:
            if "INSUFFICIENT_DATA" in str(e) or "NO_DATA_FETCHED" in str(e):
                raise
            else:
                raise ValueError(f"Data validation error: {e}")
        except Exception as e:
            raise Exception(f"Error loading data: {e}")

    def _process_network_bandwidth(self, df):
        """Convert network bandwidth to numeric scores"""
        bandwidth_mapping = {
            'Low': 5,
            'Standard': 7,
            'Medium': 7,
            'High': 9,
            'Very High': 10,
            'Ultra High': 12
        }
        
        # Create bandwidth score
        df['bandwidth_score'] = df['network_bandwidth'].map(bandwidth_mapping).fillna(7.0)
        
        print(f"✅ Processed network bandwidth")

    def _add_derived_metrics(self, df):
        """Add calculated metrics for TOPSIS analysis"""
        
        # Ensure numeric types
        numeric_cols = ['price_per_hour', 'vCPU', 'RAM_GB', 'storage_GB', 'security_score']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any NaN values with 0 for calculations
        df[numeric_cols] = df[numeric_cols].fillna(0)
        
        # Performance score (composite metric based on compute resources)
        df['performance'] = (
            (df['vCPU'] * 10) +           # CPU weight
            (df['RAM_GB'] * 2) +          # RAM weight
            (df['storage_GB'] * 0.01) +   # Storage weight
            (df.get('bandwidth_score', 7) * 5)  # Network weight
        ).fillna(1.0)
        
        # Latency score (inverse of performance - lower is better for latency)
        # Simulate latency based on region and specs
        df['latency'] = 100 / (df['performance'] + 1)  # Lower performance = higher latency
        
        # Availability score (based on provider and security)
        # Higher security typically means better availability
        df['availability'] = (df['security_score'] + 10).clip(0, 100)
        
        # Cost efficiency metrics
        df['cost_per_vcpu'] = df['price_per_hour'] / df['vCPU'].replace(0, 1)
        df['cost_per_gb_ram'] = df['price_per_hour'] / df['RAM_GB'].replace(0, 1)
        
        print(f"✅ Added derived metrics: performance, latency, availability")

    def filter_data(self, df, region, max_budget):
        """Filter data by region and budget - ONLY USE DATASET REGIONS"""
        if df.empty:
            return pd.DataFrame()  # Return empty DataFrame
        
        if region is None or max_budget is None:
            return df.copy()
        
        # Validate region exists in dataset
        available_regions = df['region'].unique().tolist()
        
        # Case-insensitive exact match
        region_lower = region.lower()
        matching_regions = df[df['region'].str.lower() == region_lower]
        
        if len(matching_regions) == 0:
            # Region not found in dataset
            raise ValueError(
                f"Region '{region}' not found in dataset. "
                f"Available regions: {', '.join(available_regions[:10])}"
            )
        
        # Filter by budget
        price_mask = (df['price_per_hour'] <= max_budget) & (df['price_per_hour'] > 0)
        region_mask = df['region'].str.lower() == region_lower
        
        filtered_df = df[region_mask & price_mask].copy()
        
        if len(filtered_df) == 0:
            min_price = df[region_mask]['price_per_hour'].min()
            raise ValueError(
                f"No instances in '{region}' under ${max_budget:.3f}/hour. "
                f"Minimum price in {region}: ${min_price:.3f}/hour"
            )
        
        print(f"🎯 Filtered: {len(filtered_df)} instances in {region} under ${max_budget}/hour")
        return filtered_df

    def prepare_decision_matrix(self, df):
        """Prepare decision matrix for TOPSIS"""
        
        # TOPSIS criteria columns - EXACT ORDER MATTERS
        criteria_columns = [
            'price_per_hour',   # Cost criterion (lower is better)
            'performance',      # Benefit criterion (higher is better)
            'security_score',   # Benefit criterion (higher is better)
            'availability',     # Benefit criterion (higher is better)
            'bandwidth_score',  # Benefit criterion (higher is better)
            'latency',          # Cost criterion (lower is better)
            'cost_per_vcpu'     # Cost criterion (lower is better)
        ]
        
        # Ensure all criteria columns exist
        for col in criteria_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column for TOPSIS: {col}")
        
        # Create decision matrix (numeric only)
        decision_matrix = df[criteria_columns].values.astype(float)
        
        # Instance information for display
        display_columns = [
            'provider', 'instance_type', 'region', 'price_per_hour',
            'vCPU', 'RAM_GB', 'storage_GB', 'security_score',
            'performance', 'availability', 'latency', 'bandwidth_score'
        ]
        
        instance_info = df[[col for col in display_columns if col in df.columns]].copy()
        
        print(f"📊 Decision matrix prepared: {decision_matrix.shape}")
        
        return decision_matrix, instance_info

    def get_dataset_statistics(self, df):
        """Get comprehensive dataset statistics"""
        if df.empty:
            return {
                'total_instances': 0,
                'providers': [],
                'regions': [],
                'min_price': 0,
                'max_price': 0,
                'avg_price': 0
            }
        
        stats = {
            'total_instances': len(df),
            'providers': df['provider'].unique().tolist() if 'provider' in df.columns else [],
            'regions': df['region'].unique().tolist() if 'region' in df.columns else [],
        }
        
        # Price statistics
        if 'price_per_hour' in df.columns:
            price_col = pd.to_numeric(df['price_per_hour'], errors='coerce').dropna()
            if len(price_col) > 0:
                stats.update({
                    'min_price': float(price_col.min()),
                    'max_price': float(price_col.max()),
                    'avg_price': float(price_col.mean())
                })
        
        return stats
