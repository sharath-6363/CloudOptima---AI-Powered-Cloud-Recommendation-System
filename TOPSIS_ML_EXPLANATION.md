# TOPSIS + XGBoost Working Flow Explanation

## 📋 Simple Explanation 

**The system uses a hybrid approach combining TOPSIS (mathematical ranking) and XGBoost (Gradient Boosting) to recommend optimal cloud instances. First, TOPSIS analyzes 3000+ instances across 7 criteria (cost, CPU, RAM, storage, security, network, performance) using weighted normalization and Euclidean distance to generate objective scores. Then, an XGBoost model trained on 4 datasets (catalog, cost, recommendations, multicloud) with high accuracy predicts user satisfaction probability for each recommendation. Finally, both scores are combined (60% TOPSIS + 40% XGBoost) to produce a hybrid ranking, ensuring recommendations are both mathematically optimal and aligned with learned user preferences.**

---

## 🔄 Technical Flow

**User Request → Load 3000 instances from 4 CSV datasets → Filter by region & budget → TOPSIS calculates mathematical ranking (56.4%) → XGBoost model predicts satisfaction probability (97.9%) → Combine scores: Hybrid = 0.6×TOPSIS + 0.4×XGBoost = 73.0% → Return top 5 ranked recommendations with AI explanation from Groq LLaMA 3.3 70B.**

---

## 📊 Detailed Step-by-Step Process

### **Step 1: Data Loading**
- Load 4 datasets: catalog_data.csv, cost_data.csv, recommendation_logs.csv, multi_cloud_strategies_dataset.csv
- Total: 3000 cloud instances from AWS, Azure, GCP, and other providers
- Merge datasets to create unified view with all features

### **Step 2: TOPSIS Analysis**
- Filter instances by user's region and budget
- Evaluate each instance across 7 criteria:
  1. Price per hour (minimize)
  2. vCPU count (maximize)
  3. RAM capacity (maximize)
  4. Storage space (maximize)
  5. Security score (maximize)
  6. Network performance (maximize)
  7. Overall performance (maximize)
- Apply user-defined weights to each criterion
- Normalize data and calculate Euclidean distance from ideal solution
- Generate TOPSIS score (0-1 scale)

### **Step 3: XGBoost Prediction**
- Load pre-trained XGBoost model from xgb_model.json
- For each recommendation, extract 5 features:
  - vCPU
  - RAM_GB
  - storage_GB
  - price_per_hour
  - risk_score
- Create DMatrix and predict probability of user satisfaction (0-1 scale)
- XGBoost model uses 100 boosting rounds with max_depth=5

### **Step 4: Hybrid Scoring**
- Combine TOPSIS and XGBoost scores:
  ```
  Hybrid Score = (0.6 × TOPSIS Score) + (0.4 × XGBoost Score)
  ```
- Example:
  - TOPSIS: 56.429%
  - XGBoost: 97.906%
  - Hybrid: (0.6 × 0.56429) + (0.4 × 0.97906) = 73.020%

### **Step 5: Ranking & Selection**
- Sort all recommendations by Hybrid Score (descending)
- Select top 5 recommendations
- Generate AI explanation using Groq LLaMA 3.3 70B
- Return results to frontend

---

## 🎯 Example Output

```
Recommendation #1 (BEST):
├── Provider: GCP
├── Instance: n2-standard-8
├── Region: us-east-1
├── Specs: 8 vCPU, 32GB RAM, 200GB Storage
├── Price: $0.104/hour
├── TOPSIS Score: 56.429%
├── XGBoost Satisfaction: 97.906%
└── Hybrid Score: 73.020% ← FINAL RANKING
```

---

## 🔑 Key Advantages

1. **TOPSIS (Mathematical)**
   - Objective, explainable ranking
   - Multi-criteria decision analysis
   - User-defined priority weights

2. **XGBoost (Gradient Boosting)**
   - Predicts user satisfaction
   - Learns from historical data
   - Fast and accurate predictions
   - Handles complex patterns

3. **Hybrid Approach**
   - Best of both worlds
   - Balanced recommendations
   - Higher user satisfaction

---

## 📈 XGBoost Model Details

- **Algorithm**: XGBoost (Gradient Boosting)
- **Boosting Rounds**: 100
- **Max Depth**: 5
- **Learning Rate**: 0.1
- **Training Data**: 343 samples (80%)
- **Test Data**: 86 samples (20%)
- **Objective**: Binary logistic classification

---

## 💾 Files Generated

1. `xgb_model.json` - Trained XGBoost model
2. `ml_feature_info.joblib` - Feature metadata
3. Recommendations stored in MySQL database

---

## 🚀 Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: Next.js (React)
- **Database**: MySQL
- **ML Library**: XGBoost
- **AI**: Groq LLaMA 3.3 70B
- **Algorithm**: TOPSIS + XGBoost

---

**Project**: CloudOptima - AI-Powered Cloud Recommendation System
**Date**: January 2025
**Status**: Complete ✅
