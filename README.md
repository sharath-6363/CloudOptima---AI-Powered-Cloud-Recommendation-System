# CloudOptima - AI-Powered Cloud Recommendation System

A comprehensive full-stack application that provides AI-powered cloud instance recommendations using TOPSIS algorithm and LLM analysis.

## 🚀 Features

- **User Authentication**: Secure login/register system with JWT tokens
- **AI Recommendations**: TOPSIS-based multi-criteria decision analysis
- **LLM Integration**: Groq API for detailed explanations and insights
- **Rating System**: Users can rate and review recommendations
- **History Tracking**: Complete recommendation history for each user
- **Modern UI**: Next.js frontend with Tailwind CSS
- **Real-time Analysis**: Interactive dashboard with live updates

## 🏗️ Architecture

### Backend (Flask API)
- **Framework**: Flask with SQLAlchemy ORM
- **Database**: MySQL for data persistence
- **Authentication**: JWT-based authentication
- **AI Engine**: Custom TOPSIS implementation + Groq LLM
- **APIs**: RESTful endpoints for all operations

### Frontend (Next.js)
- **Framework**: Next.js 14 with TypeScript
- **Styling**: Tailwind CSS with custom components
- **Icons**: React Icons (Font Awesome)
- **State Management**: React hooks
- **Authentication**: JWT token management

### Database Schema
- **Users**: Authentication and profile data
- **Recommendations**: AI-generated recommendations with TOPSIS scores
- **Ratings**: User feedback and reviews

## 📦 Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL 8.0+
- Git

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd cloud_recommendation_system
```

2. **Set up Python environment**
```bash
cd backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up MySQL database**
```bash
# Login to MySQL
mysql -u root -p

# Run the database setup script
source database_setup.sql
```

5. **Configure environment variables**
Create `.env` file in the root directory:
```env
OPENAI_API_KEY=your_groq_api_key_here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=cloud_recommendation_db
```

6. **Update database connection**
Edit `backend/app.py` line 15:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:your_password@localhost/cloud_recommendation_db'
```

7. **Run the Flask backend**
```bash
python app.py
```
Backend will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd frontend
```

2. **Install Node.js dependencies**
```bash
npm install
```

3. **Run the Next.js development server**
```bash
npm run dev
```
Frontend will run on `http://localhost:3000`

## 🎯 Usage

### 1. **Home Page**
- View application overview and features
- See user reviews and testimonials
- Access login/register options

### 2. **Authentication**
- **Register**: Create new account with username, email, password
- **Login**: Access existing account
- **Security**: JWT-based authentication with secure password hashing

### 3. **Dashboard**
- **Get Recommendations**: Configure preferences and get AI recommendations
- **History**: View past recommendations and ratings
- **Interactive UI**: Real-time updates and responsive design

### 4. **Recommendation Process**
1. **Configure Parameters**:
   - Select deployment region
   - Set budget constraints ($/hour)
   - Adjust priority weights for different criteria

2. **AI Analysis**:
   - TOPSIS algorithm analyzes 1000+ cloud instances
   - Multi-criteria evaluation (cost, CPU, memory, storage, security)
   - LLM provides detailed explanations

3. **Results**:
   - Top 5 ranked recommendations
   - Detailed specifications and pricing
   - AI-generated insights and explanations
   - Rating system for user feedback

## 🔧 API Endpoints

### Authentication
- `POST /api/register` - User registration
- `POST /api/login` - User login

### Recommendations
- `POST /api/recommend` - Get AI recommendations
- `POST /api/rate` - Rate a recommendation
- `GET /api/user/history` - Get user's recommendation history

### Public
- `GET /api/reviews` - Get public reviews
- `GET /api/stats` - Get application statistics

## 🎨 UI Components

### Modern Design Features
- **Gradient Backgrounds**: Beautiful color transitions
- **Interactive Elements**: Hover effects and animations
- **Responsive Layout**: Mobile-first design
- **Provider Badges**: Color-coded cloud provider indicators
- **Progress Indicators**: Visual feedback for all operations
- **Card-based Layout**: Clean, organized information display

### Key Pages
1. **Home**: Landing page with features and reviews
2. **Login/Register**: Authentication forms with validation
3. **Dashboard**: Main application interface with tabs
4. **Recommendations**: AI-powered analysis results
5. **History**: User's past recommendations and ratings

## 🤖 AI Features

### TOPSIS Algorithm
- **Multi-Criteria Decision Analysis**: Evaluates instances across 7 criteria
- **Weighted Scoring**: User-defined priority weights
- **Normalization**: Ensures fair comparison across different metrics
- **Ranking**: Provides objective scoring from 0-1

### LLM Integration
- **Groq API**: Fast, efficient language model processing
- **Detailed Analysis**: Comprehensive explanations of recommendations
- **Technical Insights**: Performance optimization suggestions
- **Cost Analysis**: Budget optimization recommendations

## 📊 Data Sources

The system analyzes cloud instances from:
- **AWS**: EC2 instances across multiple regions
- **Microsoft Azure**: Virtual machines with various configurations
- **Google Cloud Platform**: Compute Engine instances

### Evaluation Criteria
1. **Cost Efficiency**: Price per hour optimization
2. **CPU Performance**: vCPU count and performance
3. **Memory Capacity**: RAM allocation and efficiency
4. **Storage Options**: Disk space and performance
5. **Security Scores**: Compliance and security features
6. **Network Performance**: Bandwidth and connectivity
7. **Overall Performance**: Composite performance metrics

## 🔒 Security Features

- **Password Hashing**: Bcrypt encryption for user passwords
- **JWT Authentication**: Secure token-based authentication
- **Input Validation**: Server-side validation for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CORS Configuration**: Proper cross-origin resource sharing
- **Environment Variables**: Sensitive data stored securely

## 🚀 Deployment

### Production Setup
1. **Backend Deployment**:
   - Use Gunicorn for production WSGI server
   - Configure nginx as reverse proxy
   - Set up SSL certificates
   - Use production database (MySQL/PostgreSQL)

2. **Frontend Deployment**:
   - Build optimized production bundle: `npm run build`
   - Deploy to Vercel, Netlify, or custom server
   - Configure environment variables

3. **Database**:
   - Use managed database service (AWS RDS, Google Cloud SQL)
   - Set up automated backups
   - Configure connection pooling

## 📈 Performance Optimization

- **Database Indexing**: Optimized queries with proper indexes
- **Caching**: Redis for session and data caching
- **API Optimization**: Efficient data serialization
- **Frontend Optimization**: Code splitting and lazy loading
- **Image Optimization**: Compressed assets and modern formats

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -am 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Email: support@cloudoptima.com
- Documentation: [Wiki](link-to-wiki)

## 🔄 Version History

- **v1.0.0**: Initial release with core features
- **v1.1.0**: Added rating system and user history
- **v1.2.0**: Enhanced UI and LLM integration
- **v2.0.0**: Complete rewrite with Next.js frontend

---

**CloudOptima** - Making cloud decisions smarter with AI 🚀