# CloudOptima (AI-Powered Cloud Recommendation System)

This document is a **complete, presentation-ready explanation** of the project for an M.Tech viva / demo. It covers:
- All **frontend pages** (Next.js) and what each one does
- All major **backend API routes** (Flask) and internal modules
- The **hybrid recommendation logic** (TOPSIS + XGBoost + rating boost)
- The **rating + feedback (comment) flow**, including “no re-rate” logic

---

## 1) Problem Statement & Goal
Choosing a cloud VM/instance (AWS/Azure/GCP) is a **multi-criteria decision problem**.
A user typically wants to balance:
- **Cost** (price per hour)
- **Performance** (CPU/RAM/derived performance)
- **Security** (security score)
- **Availability**
- **Latency**
- **Network/Bandwidth**

**Goal of CloudOptima:** Given user constraints (budget + region) and preference weights, return the **top 5 best cloud instances** with:
1) A deterministic ranking,
2) Hybrid score that combines mathematical ranking + ML prediction,
3) Community rating integration (social proof),
4) Optional AI explanation (LLM) for “why option #1 is best”.

---

## 2) Tech Stack (As Implemented)

### Frontend
- **Next.js (React)** in `frontend/`
- Pages in `frontend/pages/`:
  - `index.js` (Home)
  - `login.js`
  - `register.js`
  - `dashboard.js`
- Uses `fetch()` to call Flask APIs at `http://localhost:5000/...`

### Backend
- **Flask** in `backend/app.py`
- **JWT auth** in `backend/auth.py`
- **MySQL** access via `mysql.connector` in `backend/database.py`
- Core logic modules in `backend/src/`:
  - `data_loader.py` (load + merge CSVs, compute derived features)
  - `topsis.py` (TOPSIS algorithm with tie-breaking)
  - `ml_predictor.py` (XGBoost model load + prediction)
  - `llm_module.py` (LLM prompt building + Groq API call if configured)

### ML Model
- `backend/train_ml_model.py` trains an XGBoost model and saves:
  - `backend/xgb_model.json` (trained model)
  - `backend/ml_feature_info.joblib` (feature metadata)

---

## 3) Data Pipeline (CSV → Merged Dataset → Decision Matrix)

### Source CSV files (backend/data/)
- `catalog_data.csv`: provider/instance specs (vCPU, RAM, storage, network)
- `cost_data.csv`: provider/instance pricing (price_per_hour)
- `security_data.csv`: provider/region security score

### Data merge and validation (`backend/src/data_loader.py`)
The loader:
1. Loads all CSVs
2. Validates minimum dataset size and required columns
3. Merges:
   - catalog + cost on `(provider, instance_type, region)`
   - then merges security on `(provider, region)`
4. Converts network bandwidth into a numeric **bandwidth_score**
5. Adds derived metrics:
   - `performance` (composite score from CPU, RAM, storage, network)
   - `latency` (inverse function of performance)
   - `availability` (derived from security)
   - `cost_per_vcpu`, `cost_per_gb_ram`

### Filtering (`filter_data`)
User provides:
- `region`
- `budget` ($/hour)

The loader filters to:
- exact region match (case-insensitive)
- `price_per_hour <= budget`

If the region doesn’t exist or budget is too low, it raises a clear error.

### Decision matrix (`prepare_decision_matrix`)
The TOPSIS matrix is formed from criteria (exact order matters):
1. `price_per_hour` (**cost**)
2. `performance` (**benefit**)
3. `security_score` (**benefit**)
4. `availability` (**benefit**)
5. `bandwidth_score` (**benefit**)
6. `latency` (**cost**)
7. `cost_per_vcpu` (**cost**)

---

## 4) TOPSIS Algorithm (Mathematical Ranking)

TOPSIS = “Technique for Order of Preference by Similarity to Ideal Solution”.

### Why TOPSIS?
- Handles **multiple criteria** with user weights
- Produces a **0..1 score**: higher = closer to ideal best
- Transparent and explainable in academic context

### Steps (`backend/src/topsis.py`)
Given decision matrix $X$ and weights $w$:
1) **Normalize** each criterion column using vector normalization.
2) **Weight** normalized matrix: $V = X_{norm} \cdot w$
3) Determine:
   - **ideal best** (max for benefit, min for cost)
   - **ideal worst** (min for benefit, max for cost)
4) Compute Euclidean distances to best and worst:
   - $D^+$ distance to ideal best
   - $D^-$ distance to ideal worst
5) Compute closeness coefficient:

$$
C_i = \frac{D_i^-}{D_i^+ + D_i^-}
$$

### Tie-breaking for deterministic ranking
Near-identical instances can produce identical scores. The implementation adds tiny micro-adjustments using:
- distance-to-best
- a tiny index-based epsilon

This stabilizes ranking (useful for UI consistency and reproducibility).

---

## 5) Hybrid Recommendation Logic (TOPSIS + XGBoost + Ratings)
This project is not “TOPSIS only”. It uses a **hybrid score**.

### Stage A — TOPSIS produces base ranking
In `backend/app.py`, after filtering and matrix creation:
- TOPSIS closeness scores are computed
- Data is sorted by `topsis_score` desc
- top K (max 5) are selected

Each recommendation is formatted as a JSON record containing:
- core specs (provider, instance_type, region, vCPU, RAM, storage)
- criteria metrics (security, latency, availability, bandwidth)
- `topsis_score`

### Stage B — ML (XGBoost) predicts satisfaction (loop)
If the model is loaded (`ml_predictor.is_loaded`):
- For each recommendation, XGBoost predicts `ml_satisfaction_score` ∈ [0,1]

Features used by model (as implemented in `ml_predictor.py`):
- vCPU
- RAM_GB
- storage_GB
- price_per_hour
- risk_score (defined as `1 - topsis_score` in API formatting)

### Stage C — Hybrid score formula
Hybrid score blends explainable math with learned patterns:

$$
\text{hybrid} = 0.6 \cdot \text{topsis} + 0.4 \cdot \text{xgb}
$$

A tiny tie-breaker is added to make hybrid scores deterministic when predictions match.

### Stage D — Rating boost (community feedback)
After ML enhancement, the backend adds a rating-based multiplier **only when rating_count ≥ 3** (reliability threshold):

$$
\text{ratingBoost} = (\text{avgRating}/5) \cdot 0.10
$$

Then:

$$
\text{hybrid} := \text{hybrid} \cdot (1 + \text{ratingBoost})
$$

Interpretation:
- 5★ average → up to +10% boost (if at least 3 ratings)
- 4★ average → +8% boost
- 3★ average → +6% boost

Finally, recommendations are re-sorted by `hybrid_score` desc and ranks are re-assigned.

### Why this is a good hybrid design (M.Tech perspective)
- TOPSIS gives **explainability** (MCDA)
- XGBoost gives **data-driven personalization/learning**
- Rating boost introduces **human feedback / social proof**

---

## 6) AI Explanation (LLM) and Why It Matches “Rank #1”

The system optionally generates a natural-language explanation.

### Implementation (`backend/src/llm_module.py`)
- Builds a prompt that lists the top 5 options.
- Very important detail: prompt uses positional indexing (`iloc`) to ensure:
  - **Option 1** in the prompt is exactly the **#1 ranked** recommendation.

### Provider
- If Groq SDK + `GROQ_API_KEY` exist, it calls Groq LLaMA model.
- Otherwise, it returns a clear message explaining AI is not configured.

### Why explanation is generated AFTER final ranking
The project’s final ranking can change after:
1) ML hybrid scoring
2) rating boost

So, explanation is generated **after** the final sort, ensuring the AI describes the same “#1” shown in the dashboard.

---

## 7) Backend: Complete Route-by-Route Explanation (Flask APIs)

### A) Authentication
#### `POST /api/register`
- Input: username, email, password
- Validates fields, checks duplicates
- Hashes password (bcrypt in models)
- Creates user in DB

#### `POST /api/login`
- Input: email, password
- Validates password
- Returns JWT token (7-day expiry)

**Token handling:**
- `backend/auth.py` defines `token_required` decorator.
- Protected endpoints require `Authorization: Bearer <token>`.

---

### B) Recommendation Engine
#### `POST /api/recommend` and `POST /api/recommendations`
(These are aliases pointing to the same logic.)

**Input (typical):**
- budget (max $/hour)
- region
- weights/priorities

**Processing pipeline (high-level):**
1) Load and merge dataset
2) Filter by region + budget
3) Build decision matrix
4) Normalize weights
5) Run TOPSIS
6) Select top 5
7) Attach rating info:
   - `avg_rating`, `rating_count`
   - `user_rating`, `user_has_rated`
8) If XGBoost is loaded:
   - compute `ml_satisfaction_score`
   - compute `hybrid_score`
9) Apply rating boost to hybrid score
10) Sort by hybrid score and assign ranks
11) Generate AI explanation (optional)

**Output:**
- `recommendations`: list of 5 ranked instances
- scores: `topsis_score`, `ml_satisfaction_score`, `hybrid_score`
- rating fields: `avg_rating`, `rating_count`, `user_rating`, `user_has_rated`
- AI explanation (if enabled)

---

### C) Reviews
#### `GET /api/reviews`
- Returns public review feed for home page and dashboard reviews tab.
- Joins:
  - `rating` table
  - `user` table
  - `recommendation` table (left join)

#### `POST /api/reviews`
- Creates a review (legacy style) using `Review.create()` in `backend/models.py`.
- Inserts a recommendation row (with placeholder values) and then a rating with comment.

---

### D) Ratings (Main rating workflow used by dashboard)
#### `POST /api/ratings` (Protected)
Purpose: user can rate an instance **only once**.

**Input (from dashboard modal):**
- provider
- instance_type
- rating (1..5)
- comment (optional)
- required recommendation fields (to satisfy DB schema):
  - region
  - price_per_hour
  - vCPU
  - RAM_GB
  - storage_GB
  - security_score
  - topsis_score

**Key logic:**
1) Validate rating and required fields
2) Prevent duplicates:
   - `UserRating.check_user_rated(user_id, provider, instance_type)`
   - if already rated → returns 409
3) Insert a complete `recommendation` row (NOT NULL safe)
4) Insert a `rating` row linked to `recommendation_id`

**No re-rate policy:**
- DB has unique constraint: `(user_id, recommendation_id)`
- API also checks “already rated” by provider + instance_type to keep UX simple.

#### `GET /api/user/ratings` (Protected)
- Returns the logged-in user’s ratings.

---

### E) Dataset / System Info
#### `GET /api/regions`
- Returns list of available regions from dataset.

#### `GET /api/dataset-info`
- Returns dataset statistics.

#### `GET /api/debug-data`
- Debug endpoint to inspect loaded dataset and validate columns.

#### `GET /api/stats`
- Used by home page to show counters (users/recommendations/providers).

#### `GET /api/health`
- Health check endpoint to confirm server is running.

---

## 8) Database Design (MySQL)
File: `backend/database_setup.sql`

### Tables
1) `user`
- id, username, email, password_hash, created_at

2) `recommendation`
- Stores a recommendation snapshot used for rating/reviews.
- Has many NOT NULL fields: region, price, vcpu, ram, storage, security_score, topsis_score.

3) `rating`
- user_id, recommendation_id, rating, comment
- Unique constraint: one rating per (user, recommendation)

### Why recommendation is stored when rating
Even if recommendation lists are computed dynamically, storing a recommendation snapshot allows:
- consistent history
- linking ratings to a stable record
- later analytics on what was recommended

---

## 9) Frontend Pages (Complete Explanation)

### 1) Home Page — `frontend/pages/index.js`
What it shows:
- Project branding / hero section
- Recent recommendations/reviews animation
- Stats counters

APIs used:
- `GET /api/reviews` (public feed)
- `GET /api/stats`

### 2) Login Page — `frontend/pages/login.js`
- Takes email + password
- Calls `POST /api/login`
- Stores `token` and `user` in `localStorage`
- Redirects to `/dashboard`

### 3) Register Page — `frontend/pages/register.js`
- Takes username, email, password, confirmPassword
- Validates password length and matching
- Calls `POST /api/register`
- Redirects to `/login?registered=true`

### 4) Dashboard Page — `frontend/pages/dashboard.js`
This is the main working page:
- Collects user preferences (budget, region, weights)
- Calls `POST /api/recommendations`
- Displays top recommendations (table + top card)
- Shows AI explanation text
- Provides rating modal to rate an instance

Rating behavior:
- Each recommendation row includes `avg_rating`, `rating_count`, `user_has_rated`, `user_rating`.
- If the user already rated, UI disables rating.
- When rating is submitted successfully, UI updates state **without page reload**.

---

## 10) End-to-End Demo Flow (What to Show Tomorrow)

### Step 1 — Register/Login
- Use Register page → then Login
- Show token stored in browser localStorage

### Step 2 — Generate recommendations
- Open Dashboard
- Set region and budget
- Adjust weights (tell examiner: weights = importance of criteria)

### Step 3 — Explain ranking
- Show table ranks 1..5
- Explain:
  1) TOPSIS computes base scores
  2) XGBoost predicts satisfaction and hybrid score
  3) rating boost adjusts final score

### Step 4 — Rate an option
- Click “Rate” in table
- Submit stars + optional feedback
- Show:
  - It cannot be rated again (disabled)
  - community rating count increases

### Step 5 — AI explanation
- Show that explanation matches top-ranked #1.
- Mention Groq is optional; if not configured, fallback message appears.

---

## 11) Key Formulas (Quick Viva Notes)

### TOPSIS closeness
$$
C_i = \frac{D_i^-}{D_i^+ + D_i^-}
$$

### Hybrid score
$$
H_i = 0.6 \cdot C_i + 0.4 \cdot M_i
$$
Where $M_i$ is XGBoost satisfaction probability.

### Rating boost
$$
H_i := H_i \cdot (1 + (\text{avgRating}/5) \cdot 0.10)
$$
(only if rating_count ≥ 3)

---

## 12) How to Run (Local)

### Backend
1) `cd backend`
2) `pip install -r requirements.txt`
3) Setup MySQL using `backend/database_setup.sql`
4) Run: `python app.py`

Environment variables (recommended in `.env`):
- `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- `SECRET_KEY`
- `GROQ_API_KEY` (optional)

### Frontend
1) `cd frontend`
2) `npm install`
3) Run: `npm run dev`

---

## 13) Future Enhancements (Good to Mention in Viva)
- Store recommendation history per user for full audit trail
- Use real cloud provider APIs for live pricing
- Improve EnhancedTOPSIS personalization (currently stub)
- Add explainable feature importance for XGBoost predictions
- Add pagination/search for reviews

---

## Appendix: Project Folder Map (Quick Reference)
- `backend/app.py` — API routes + orchestration (TOPSIS → ML → ratings → LLM)
- `backend/src/data_loader.py` — CSV load + merge + derived metrics
- `backend/src/topsis.py` — TOPSIS implementation
- `backend/src/ml_predictor.py` — load `xgb_model.json` and predict in loop
- `backend/src/llm_module.py` — LLM prompt + Groq integration
- `backend/models.py` — user/review/rating DB operations
- `backend/database_setup.sql` — schema
- `frontend/pages/index.js` — home page
- `frontend/pages/login.js` — login
- `frontend/pages/register.js` — register
- `frontend/pages/dashboard.js` — recommendations + rating modal
