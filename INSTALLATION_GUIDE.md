# 📦 CloudOptima - Complete Installation Guide

## Step-by-Step Installation on Any Device

---

## 📋 Prerequisites (Install These First)

### 1. **Python 3.8+**
- Download: https://www.python.org/downloads/
- During installation: ✅ Check "Add Python to PATH"
- Verify: `python --version`

### 2. **Node.js 16+**
- Download: https://nodejs.org/
- Install LTS version
- Verify: `node --version` and `npm --version`

### 3. **MySQL 8.0+**
- Download: https://dev.mysql.com/downloads/mysql/
- Remember your root password during installation
- Verify: `mysql --version`

### 4. **Git**
- Download: https://git-scm.com/downloads
- Verify: `git --version`

---

## 🚀 Installation Steps

### **Step 1: Clone the Project**

```bash
# Open terminal/command prompt
cd Desktop/Projects

# Clone repository
git clone <repository-url>
cd cloud_recommendation_system
```

**If you have ZIP file instead:**
```bash
# Extract ZIP file to Desktop/Projects/
cd Desktop/Projects/cloud_recommendation_system
```

---

### **Step 2: Setup MySQL Database**

#### **2.1 Login to MySQL**
```bash
mysql -u root -p
# Enter your MySQL password
```

#### **2.2 Create Database**
```sql
CREATE DATABASE cloud_recommendation_db;
USE cloud_recommendation_db;
```

#### **2.3 Run Database Setup Script**

**Option A - From MySQL prompt:**
```sql
SOURCE database_setup.sql;
```

**Option B - From terminal:**
```bash
# Windows
Get-Content database_setup.sql | mysql -u root -p

# Linux/Mac
mysql -u root -p < database_setup.sql
```

#### **2.4 Verify Tables Created**
```sql
SHOW TABLES;
# Should show: users, recommendations, ratings
```

---

### **Step 3: Setup Backend (Flask API)**

#### **3.1 Navigate to Backend**
```bash
cd backend
```

#### **3.2 Create Virtual Environment**

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**You should see `(venv)` in your terminal**

#### **3.3 Install Python Dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**This installs:**
- Flask (web framework)
- XGBoost (machine learning)
- MySQL connector
- Groq API
- And all other dependencies

**⏱️ Takes 2-5 minutes**

#### **3.4 Configure Environment Variables**

Create `.env` file in project root:

**Windows:**
```bash
cd ..
notepad .env
```

**Linux/Mac:**
```bash
cd ..
nano .env
```

**Add this content:**
```env
OPENAI_API_KEY=your_groq_api_key_here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=cloud_recommendation_db
```

**Replace:**
- `your_groq_api_key_here` → Get from https://console.groq.com/
- `your_mysql_password` → Your MySQL root password

#### **3.5 Update Database Connection in app.py**

Open `backend/app.py` and find line 15:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:your_password@localhost/cloud_recommendation_db'
```

**Replace `your_password` with your MySQL password**

#### **3.6 Train XGBoost Model**
```bash
cd backend
python train_ml_model.py
```

**Expected Output:**
```
🤖 TRAINING XGBOOST MODEL
✅ Loaded 3000 instances from catalog
✅ Training completed!
✅ XGBoost model saved to: xgb_model.json
```

**Creates:**
- `xgb_model.json` (50-100 KB)
- `ml_feature_info.joblib`

#### **3.7 Start Backend Server**
```bash
python app.py
```

**Expected Output:**
```
📦 Loading XGBoost model from xgb_model.json...
✅ XGBoost model loaded successfully!
 * Running on http://localhost:5000
```

**✅ Backend is running! Keep this terminal open.**

---

### **Step 4: Setup Frontend (Next.js)**

#### **4.1 Open New Terminal**
Keep backend running, open a **NEW** terminal/command prompt

#### **4.2 Navigate to Frontend**
```bash
cd Desktop/Projects/cloud_recommendation_system/frontend
```

#### **4.3 Install Node Dependencies**
```bash
npm install
```

**This installs:**
- Next.js
- React
- Tailwind CSS
- All frontend libraries

**⏱️ Takes 3-10 minutes**

#### **4.4 Start Frontend Server**
```bash
npm run dev
```

**Expected Output:**
```
✓ Ready in 2.5s
○ Local: http://localhost:3000
```

**✅ Frontend is running!**

---

## 🎯 Access the Application

### **Open Browser:**
```
http://localhost:3000
```

### **You should see:**
- ✅ CloudOptima home page
- ✅ Login/Register buttons
- ✅ Features and reviews

### **Test the System:**
1. Click "Get Started" or "Login"
2. Register new account
3. Login with credentials
4. Go to Dashboard
5. Click "Get Recommendations"
6. Configure preferences
7. Get AI-powered recommendations!

---

## 📁 Project Structure

```
cloud_recommendation_system/
├── backend/                    # Flask API
│   ├── app.py                 # Main server (PORT 5000)
│   ├── train_ml_model.py      # XGBoost training
│   ├── xgb_model.json         # Trained model ✅
│   ├── requirements.txt       # Python dependencies
│   ├── data/                  # CSV datasets
│   │   ├── catalog_data.csv
│   │   ├── cost_data.csv
│   │   ├── recommendation_logs.csv
│   │   └── multi_cloud_strategies_dataset.csv
│   └── src/                   # Source code
│       ├── topsis.py          # TOPSIS algorithm
│       └── ml_predictor.py    # XGBoost predictor
│
├── frontend/                   # Next.js app
│   ├── package.json           # Node dependencies
│   ├── pages/                 # React pages
│   ├── components/            # React components
│   └── styles/                # CSS styles
│
├── database_setup.sql         # MySQL schema
├── .env                       # Environment variables
└── README.md                  # Project documentation
```

---

## 🔧 Troubleshooting

### **Problem 1: MySQL Connection Error**
```
Error: Can't connect to MySQL server
```

**Solution:**
1. Check MySQL is running: `mysql --version`
2. Verify password in `app.py` line 15
3. Verify password in `.env` file
4. Test connection: `mysql -u root -p`

---

### **Problem 2: XGBoost Model Not Found**
```
⚠️ XGBoost model file not found: xgb_model.json
```

**Solution:**
```bash
cd backend
python train_ml_model.py
```

---

### **Problem 3: Port Already in Use**
```
Error: Port 5000 is already in use
```

**Solution:**

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -ti:5000 | xargs kill -9
```

---

### **Problem 4: Module Not Found**
```
ModuleNotFoundError: No module named 'xgboost'
```

**Solution:**
```bash
# Activate virtual environment first!
cd backend
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Then install
pip install xgboost==2.0.3
```

---

### **Problem 5: npm install fails**
```
Error: EACCES permission denied
```

**Solution:**

**Windows:** Run terminal as Administrator

**Linux/Mac:**
```bash
sudo npm install
```

---

### **Problem 6: Groq API Key Missing**
```
Error: OPENAI_API_KEY not found
```

**Solution:**
1. Get API key from https://console.groq.com/
2. Add to `.env` file:
   ```
   OPENAI_API_KEY=gsk_xxxxxxxxxxxxx
   ```
3. Restart backend server

---

## ✅ Verification Checklist

Before running the application, verify:

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] MySQL 8.0+ installed and running
- [ ] Database `cloud_recommendation_db` created
- [ ] Tables created (users, recommendations, ratings)
- [ ] Virtual environment activated
- [ ] All Python packages installed (`pip list`)
- [ ] XGBoost model trained (`xgb_model.json` exists)
- [ ] `.env` file created with correct values
- [ ] `app.py` has correct MySQL password
- [ ] Backend running on http://localhost:5000
- [ ] All Node packages installed (`node_modules/` exists)
- [ ] Frontend running on http://localhost:3000
- [ ] Can access home page in browser

---

## 🎓 For Your Teacher

### **Show These Files:**
1. `xgb_model.json` - Trained XGBoost model
2. `train_ml_model.py` - Training script
3. `ml_predictor.py` - Model loading and usage
4. `app.py` - Flask API with ML integration

### **Demonstrate:**
1. **Model Training:**
   ```bash
   python train_ml_model.py
   ```
   Shows: Model saved to `xgb_model.json`

2. **Model Loading:**
   ```bash
   python app.py
   ```
   Shows: "XGBoost model loaded successfully!"

3. **Model Usage:**
   - Make recommendation request
   - Shows: "Enhancing recommendations with XGBoost..."
   - Returns: TOPSIS + XGBoost hybrid scores

---

## 📊 System Requirements

### **Minimum:**
- CPU: 2 cores
- RAM: 4 GB
- Storage: 2 GB free space
- Internet: For API calls

### **Recommended:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 5 GB free space
- Internet: Stable connection

---

## 🚀 Quick Start Commands

### **First Time Setup:**
```bash
# 1. Clone project
git clone <repo-url>
cd cloud_recommendation_system

# 2. Setup database
mysql -u root -p < database_setup.sql

# 3. Setup backend
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python train_ml_model.py
python app.py

# 4. Setup frontend (new terminal)
cd frontend
npm install
npm run dev
```

### **Daily Usage:**
```bash
# Terminal 1 - Backend
cd backend
venv\Scripts\activate
python app.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

---

## 📞 Support

### **Common Issues:**
- Database connection → Check MySQL password
- Module not found → Activate virtual environment
- Port in use → Kill process or use different port
- API errors → Check Groq API key

### **Resources:**
- Python: https://docs.python.org/
- Node.js: https://nodejs.org/docs/
- MySQL: https://dev.mysql.com/doc/
- XGBoost: https://xgboost.readthedocs.io/
- Next.js: https://nextjs.org/docs

---

## 🎉 Success!

If you can:
- ✅ Access http://localhost:3000
- ✅ Register and login
- ✅ Get recommendations
- ✅ See TOPSIS + XGBoost scores

**Your installation is complete!** 🚀

---

**CloudOptima** - AI-Powered Cloud Recommendation System
**Version:** 2.0.0 with XGBoost
**Last Updated:** January 2025
