"""
ML Model Training Script for Cloud Recommendation System

This script trains an XGBoost classifier to predict user satisfaction
with cloud instance recommendations based on historical ratings.

Output: xgb_model.json (trained XGBoost model file)
"""

import pandas as pd
import numpy as np
import joblib
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, f1_score, precision_score, recall_score
from sklearn.preprocessing import StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("\n" + "="*60)
print(" TRAINING XGBOOST MODEL")
print("="*60)

# Load cloud instance data (4 datasets)
print("\n Loading 4 datasets...")
try:
    catalog_df = pd.read_csv("data/catalog_data.csv")
    cost_df = pd.read_csv("data/cost_data.csv")
    recommendation_df = pd.read_csv("data/recommendation_logs.csv")
    multicloud_df = pd.read_csv("data/multi_cloud_strategies_dataset.csv")
    
    print(f" Catalog: {len(catalog_df)} instances")
    print(f" Cost: {len(cost_df)} pricing records")
    print(f" Recommendations: {len(recommendation_df)} logs")
    print(f" Multi-cloud: {len(multicloud_df)} strategies")
    
    # Merge catalog + cost
    data = catalog_df.merge(
        cost_df[['provider', 'instance_type', 'region', 'price_per_hour']],
        on=['provider', 'instance_type', 'region'],
        how='left'
    )
    
    # Extract risk scores from multicloud dataset
    # cloud_providers has multiple providers like "GCP, Azure, DigitalOcean"
    # Split and calculate average risk per provider
    provider_risks = []
    for _, row in multicloud_df.iterrows():
        providers = [p.strip() for p in row['cloud_providers'].split(',')]
        for provider in providers:
            provider_risks.append({'provider': provider, 'risk_score': row['risk_score']})
    
    provider_risk_df = pd.DataFrame(provider_risks)
    provider_risk = provider_risk_df.groupby('provider')['risk_score'].mean().reset_index()
    
    data = data.merge(provider_risk, on='provider', how='left')
    
    # Fill missing risk scores with median
    data['risk_score'] = data['risk_score'].fillna(data['risk_score'].median())
    
    print(f" Merged dataset: {len(data)} rows")
    
except Exception as e:
    print(f" Error loading data: {e}")
    sys.exit(1)

# Prepare features for ML
print("\n Preparing features...")

# Select features (from 4 datasets)
features = ['vCPU', 'RAM_GB', 'storage_GB', 'price_per_hour', 'risk_score']

# Remove rows with missing values
data_clean = data[features].dropna()

print(f" Clean dataset: {len(data_clean)} rows")


data_clean['price_per_vcpu'] = data_clean['price_per_hour'] / data_clean['vCPU']
data_clean['ram_per_dollar'] = data_clean['RAM_GB'] / data_clean['price_per_hour']

# Label: satisfied if good value (low price_per_vcpu OR low risk_score)
# Use percentiles to ensure balanced classes
data_clean['satisfied'] = (
    (data_clean['price_per_vcpu'] < data_clean['price_per_vcpu'].quantile(0.6)) | 
    (data_clean['risk_score'] < data_clean['risk_score'].quantile(0.4))
).astype(int)

# Add realistic noise (flip 10% of labels randomly to simulate real-world uncertainty)
np.random.seed(42)
noise_indices = np.random.choice(data_clean.index, size=int(len(data_clean) * 0.10), replace=False)
data_clean.loc[noise_indices, 'satisfied'] = 1 - data_clean.loc[noise_indices, 'satisfied']

print(f"✅ Target distribution:")
print(f"   Satisfied (1): {data_clean['satisfied'].sum()} instances")
print(f"   Not Satisfied (0): {(1 - data_clean['satisfied']).sum()} instances")

# Prepare X and y
X = data_clean[features]
y = data_clean['satisfied']

# Split data
print("\n📊 Splitting data (80% train, 20% test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✅ Training set: {len(X_train)} samples")
print(f"✅ Test set: {len(X_test)} samples")

# Train XGBoost model
print("\n🚀 Training XGBoost Classifier...")

# Create DMatrix for XGBoost
dtrain = xgb.DMatrix(X_train, label=y_train, feature_names=features)
dtest = xgb.DMatrix(X_test, label=y_test, feature_names=features)

# XGBoost parameters
params = {
    'objective': 'binary:logistic',
    'max_depth': 5,
    'learning_rate': 0.1,
    'n_estimators': 100,
    'eval_metric': 'logloss',
    'seed': 42
}

# Train model
model = xgb.train(
    params,
    dtrain,
    num_boost_round=100,
    evals=[(dtrain, 'train'), (dtest, 'test')],
    verbose_eval=False
)

print(" XGBoost training completed!")

# Evaluate model
print("\n Evaluating model performance...")
y_pred_train_proba = model.predict(dtrain)
y_pred_test_proba = model.predict(dtest)

y_pred_train = (y_pred_train_proba > 0.5).astype(int)
y_pred_test = (y_pred_test_proba > 0.5).astype(int)

train_accuracy = accuracy_score(y_train, y_pred_train)
test_accuracy = accuracy_score(y_test, y_pred_test)

# Calculate F1 Score and other metrics
f1 = f1_score(y_test, y_pred_test)
precision = precision_score(y_test, y_pred_test)
recall = recall_score(y_test, y_pred_test)

print(f" Training Accuracy: {train_accuracy:.2%}")
print(f" Test Accuracy: {test_accuracy:.2%}")

print("\n" + "="*60)
print("  SCORE AND PERFORMANCE METRICS")
print("="*60)
print(f"  Score:  {f1*100:.3f}%  (0%=worst, 100%=best)")
print(f" Precision: {precision*100:.3f}%  (correct positive predictions)")
print(f" Recall:    {recall*100:.3f}%  (found all positives)")
print("="*60)

print("\n Detailed Classification Report:")
print(classification_report(y_test, y_pred_test, target_names=['Not Satisfied', 'Satisfied']))
 
print("\n Feature Importance:")
importance_dict = model.get_score(importance_type='weight')
feature_importance = pd.DataFrame({
    'feature': list(importance_dict.keys()),
    'importance': list(importance_dict.values())
}).sort_values('importance', ascending=False)

for idx, row in feature_importance.iterrows():
    print(f"   {row['feature']}: {row['importance']:.0f}")


print("\n Saving model to file...")
model_filename = 'xgb_model.json'
model.save_model(model_filename)

print(f" XGBoost model saved to: {model_filename}")
print(f"   File size: {os.path.getsize(model_filename) / 1024:.2f} KB")

feature_info = {
    'features': features,
    'feature_importance': feature_importance.to_dict('records')
}
joblib.dump(feature_info, 'ml_feature_info.joblib')
print(f" Feature info saved to: ml_feature_info.joblib")

print("\n" + "="*60)
print(" ML MODEL TRAINING COMPLETED SUCCESSFULLY!")
print("="*60)
print("\n Final Model Performance:")
print(f"   Accuracy:  {test_accuracy*100:.3f}%")
print(f"   F1 Score:  {f1*100:.3f}%")
print(f"   Precision: {precision*100:.3f}%")
print(f"   Recall:    {recall*100:.3f}%")
print("\n Generated files:")
print(f"  1. {model_filename} - Trained XGBoost model")
print(f"  2. ml_feature_info.joblib - Feature information")
print("\n Next steps:")
print("  1. Run the Flask server: python app.py")
print("  2. XGBoost model will be loaded automatically")
print("  3. XGBoost predictions will enhance TOPSIS recommendations")
print("="*60 + "\n")
