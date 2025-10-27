# 🎯 ABIS - AI-Based Interview System

**ABIS** (AI-Based Interview System) adalah sistem wawancara berbasis AI yang menggunakan teknologi advanced untuk analisis kandidat secara objektif dan komprehensif.

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Requirements](#-requirements)
- [Installation (Local Development)](#-installation-local-development)
- [Deployment to VPS Linux](#-deployment-to-vps-linux)
- [Configuration](#-configuration)
- [Usage Guide](#-usage-guide)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)

---

## 🎨 Features

### Core Features
- ✅ **Live Interview Recording** - Record with webcam & audio
- ✅ **AI Transcription** - Whisper large-v2 model for accurate speech-to-text
- ✅ **Dual Emotion Detection** - Facial (DeepFace) + Speech emotions
- ✅ **Hybrid Semantic Analysis** - Exact + AI-based matching for accurate assessment
- ✅ **Custom Indicators** - Define interview criteria per position
- ✅ **AI Assessment** - Automatic scoring with reasoning
- ✅ **Manual Scoring** - Override AI scores with manual input
- ✅ **Dynamic Score Calculation** - AI (60%) + Manual (40%) weighted scoring

### Advanced Features
- ✅ **Dashboard Analytics** - Comprehensive statistics and insights
- ✅ **AI Hiring Recommendations** - 5 decision levels with confidence scores
- ✅ **Candidate Comparison** - Side-by-side candidate analysis
- ✅ **Interview Transcript Viewer** - Full transcript with matched sentences
- ✅ **Real-time Audio Visualizer** - Waveform visualization during recording
- ✅ **Timer & Stopwatch** - Track interview duration
- ✅ **Emotion Charts** - Separated facial and speech emotion tracking
- ✅ **Audio Cleanup** - Automatic file management

### UI/UX Features
- ✅ **Professional Dashboard** - Clean, simple, presentation-ready
- ✅ **Responsive Design** - Works on desktop and mobile
- ✅ **Pagination** - Efficient data browsing (10/20/50/100 items)
- ✅ **Real-time Feedback** - Toast notifications for all actions
- ✅ **Loading States** - Clear indicators for async operations

---

## 🛠 Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** MySQL 8.0+
- **ORM:** SQLAlchemy 2.0
- **Authentication:** JWT (python-jose)
- **AI Models:**
  - Whisper Large-v2 (faster-whisper)
  - DeepFace (emotion detection)
  - Sentence Transformers (semantic analysis)

### Frontend
- **Framework:** React 18 + Vite
- **State Management:** Zustand
- **Styling:** Tailwind CSS
- **Charts:** Recharts
- **Routing:** React Router v6
- **HTTP Client:** Axios

---

## 📦 Requirements

### System Requirements
- **OS:** Windows 10+, Ubuntu 20.04+, or macOS 12+
- **RAM:** Minimum 8GB (16GB recommended for AI processing)
- **Storage:** 10GB free space (for AI models)
- **CPU:** Multi-core processor recommended

### Software Requirements
- **Python:** 3.10 or 3.11 (3.12+ not tested)
- **Node.js:** 18.x or 20.x
- **MySQL:** 8.0+
- **FFmpeg:** Required for audio processing

---

## 🚀 Installation (Local Development)

### 1. Clone Repository

```bash
git clone https://github.com/synchromes/abis.git
cd abis
```

### 2. Backend Setup

#### Install Python Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Install FFmpeg

**Windows (using Chocolatey):**
```bash
choco install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS (using Homebrew):**
```bash
brew install ffmpeg
```

#### Setup Database

1. Create MySQL database:
```sql
CREATE DATABASE abis_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Create `.env` file in `backend/`:
```env
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/abis_interview

# JWT Authentication
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# File Upload
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600

# AI Models
WHISPER_MODEL=large-v2
WHISPER_DEVICE=cpu
DEEPFACE_BACKEND=opencv
```

3. Run migrations:
```bash
# Apply migrations
python -m alembic upgrade head
```

4. Create initial user:
```bash
python create_admin.py
```

#### Run Backend Server

```bash
# Development
python run.py

# Production (using Gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

Backend will run at: `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

#### Run Frontend Dev Server

```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

Frontend will run at: `http://localhost:5173` or `http://localhost:3000`

---

## 🌐 Deployment to VPS Linux

### Prerequisites

- Ubuntu 20.04+ VPS
- Root or sudo access
- Domain name (optional but recommended)
- Minimum 4GB RAM, 2 CPU cores

### 1. Initial Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.10 python3-pip python3-venv \
    mysql-server nginx supervisor git curl \
    ffmpeg build-essential libmysqlclient-dev
```

### 2. Install Node.js

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 3. Setup MySQL

```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database
sudo mysql -u root -p
```

```sql
CREATE DATABASE abis_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'abis_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON abis_interview.* TO 'abis_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Clone and Setup Application

```bash
# Create app directory
sudo mkdir -p /var/www/abis
sudo chown $USER:$USER /var/www/abis
cd /var/www/abis

# Clone repository
git clone https://github.com/synchromes/abis.git .

# Setup backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Create production .env
nano .env
```

Production `.env`:
```env
DATABASE_URL=mysql+pymysql://abis_user:your_strong_password@localhost:3306/abis_interview
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=https://yourdomain.com
UPLOAD_DIR=/var/www/abis/uploads
MAX_FILE_SIZE=104857600
WHISPER_MODEL=large-v2
WHISPER_DEVICE=cpu
DEEPFACE_BACKEND=opencv
```

```bash
# Create uploads directory
mkdir -p /var/www/abis/uploads
chmod 755 /var/www/abis/uploads

# Run migrations
python -m alembic upgrade head

# Create admin user
python create_admin.py
```

### 5. Setup Frontend

```bash
cd /var/www/abis/frontend

# Install dependencies
npm install

# Create production .env
nano .env
```

```env
VITE_API_URL=https://yourdomain.com/api
```

```bash
# Build for production
npm run build
```

### 6. Configure Supervisor (Backend)

```bash
sudo nano /etc/supervisor/conf.d/abis-backend.conf
```

```ini
[program:abis-backend]
directory=/var/www/abis/backend
command=/var/www/abis/backend/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/abis-backend.log
stderr_logfile=/var/log/abis-backend-error.log
environment=PATH="/var/www/abis/backend/venv/bin"
```

```bash
# Update supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start abis-backend
```

### 7. Configure Nginx

```bash
sudo nano /etc/nginx/sites-available/abis
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    client_max_body_size 100M;

    # Frontend
    location / {
        root /var/www/abis/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # API Docs
    location /docs {
        proxy_pass http://127.0.0.1:8000/docs;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Uploads
    location /uploads/ {
        alias /var/www/abis/uploads/;
        autoindex off;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/abis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Setup SSL (Optional but Recommended)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal is configured automatically
```

### 9. Setup Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 10. Verify Deployment

```bash
# Check backend status
sudo supervisorctl status abis-backend

# Check backend logs
sudo tail -f /var/log/abis-backend.log

# Check Nginx
sudo systemctl status nginx
```

Visit: `https://yourdomain.com`

---

## ⚙️ Configuration

### Backend Configuration

All backend configuration is in `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | MySQL connection string | - |
| `SECRET_KEY` | JWT secret key | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | 30 |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | * |
| `UPLOAD_DIR` | Upload directory path | uploads |
| `MAX_FILE_SIZE` | Max file size in bytes | 100MB |
| `WHISPER_MODEL` | Whisper model size | large-v2 |
| `WHISPER_DEVICE` | Processing device | cpu |
| `DEEPFACE_BACKEND` | Face detection backend | opencv |

### Frontend Configuration

Frontend configuration in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API URL | http://localhost:8000/api |

---

## 📖 Usage Guide

### 1. Login

Default credentials (change after first login):
- **Username:** admin
- **Password:** admin123

### 2. Create Interview

1. Go to **Interviews** page
2. Click **"+ Buat Interview Baru"**
3. Fill in candidate details:
   - Name
   - Position
   - Email (optional)
   - Phone (optional)
   - Notes (optional)
4. Click **"Simpan"**

### 3. Setup Interview Indicators

1. Open interview details
2. Go to **"Indikator Penilaian"** tab
3. Add indicators with:
   - Name (e.g., "Kemampuan Komunikasi")
   - Description (what to look for)
   - Weight (1-10, higher = more important)
   - Keywords (comma-separated, for semantic matching)

### 4. Conduct Interview

1. Click **"Mulai Wawancara"**
2. Grant camera and microphone permissions
3. Interview recording starts with:
   - Live video preview
   - Audio waveform visualization
   - Timer/stopwatch
4. Click **"Selesai"** when done

### 5. Process Interview

1. After recording, click **"Process Interview"**
2. AI will:
   - Transcribe audio (using Whisper)
   - Detect emotions (facial + speech)
   - Analyze answers against indicators
   - Generate scores and recommendations
3. Processing takes ~2-5 minutes depending on interview length

### 6. Review Assessment

1. Go to **"Assessment"** tab
2. Review:
   - AI scores per indicator
   - Evidence from transcript
   - Reasoning
   - Emotion charts
3. Optionally add **Manual Scores** to override AI

### 7. View Dashboard

- **Dashboard Overview** shows:
  - Total interviews
  - Completion rate
  - Average scores
  - AI success rate
  - Score distribution chart
  - Top 5 candidates
  - Quick actions

---

## 📚 API Documentation

### Access API Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Main Endpoints

#### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register new user
- `GET /api/auth/me` - Get current user

#### Interviews
- `GET /api/interviews/` - List interviews (with pagination)
- `POST /api/interviews/` - Create interview
- `GET /api/interviews/{id}` - Get interview details
- `POST /api/interviews/{id}/start` - Start interview
- `POST /api/interviews/{id}/complete` - Complete interview
- `POST /api/interviews/{id}/process` - Process interview with AI
- `DELETE /api/interviews/{id}` - Delete interview

#### Dashboard & Analytics
- `GET /api/interviews/dashboard/statistics` - Get dashboard stats
- `GET /api/interviews/compare?interview_ids=1,2` - Compare candidates
- `GET /api/interviews/{id}/recommendations` - Get AI recommendations
- `GET /api/interviews/{id}/transcript` - Get full transcript

#### Indicators
- `GET /api/interviews/{id}/indicators` - Get indicators
- `POST /api/interviews/{id}/indicators` - Add indicator
- `DELETE /api/interviews/{id}/indicators/{indicator_id}` - Delete indicator

#### Scoring
- `GET /api/interviews/{id}/assessment` - Get assessment results
- `PUT /api/interviews/{id}/manual-scores` - Update manual scores
- `POST /api/interviews/recalculate-scores` - Recalculate all scores

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Backend won't start

**Error:** `ModuleNotFoundError: No module named 'faster_whisper'`

**Solution:**
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

#### 2. Database connection error

**Error:** `Can't connect to MySQL server`

**Solution:**
- Check MySQL is running: `sudo systemctl status mysql`
- Verify credentials in `.env`
- Test connection: `mysql -u abis_user -p abis_interview`

#### 3. Frontend can't connect to backend

**Error:** `Network Error` or `CORS Error`

**Solution:**
- Check backend is running: `http://localhost:8000/docs`
- Verify `VITE_API_URL` in frontend `.env`
- Check `CORS_ORIGINS` in backend `.env`

#### 4. Processing fails

**Error:** `Whisper model not found` or `Processing failed`

**Solution:**
- Ensure FFmpeg is installed: `ffmpeg -version`
- Check sufficient RAM (8GB+ for large-v2 model)
- Review logs: `sudo tail -f /var/log/abis-backend.log`

#### 5. Upload fails

**Error:** `413 Request Entity Too Large`

**Solution:**
- Increase Nginx limit:
```nginx
client_max_body_size 100M;
```
- Restart Nginx: `sudo systemctl restart nginx`

#### 6. Scores showing 0

**Solution:**
```bash
# Use recalculate endpoint via Swagger UI
# Or re-process the interview
```

---

## 🔄 Maintenance

### Update Application

```bash
cd /var/www/abis
git pull origin main

# Update backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python -m alembic upgrade head
sudo supervisorctl restart abis-backend

# Update frontend
cd ../frontend
npm install
npm run build
```

### Backup Database

```bash
# Backup
mysqldump -u abis_user -p abis_interview > backup_$(date +%Y%m%d).sql

# Restore
mysql -u abis_user -p abis_interview < backup_20250127.sql
```

### Monitor Logs

```bash
# Backend logs
sudo tail -f /var/log/abis-backend.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Check Status

```bash
# Backend
sudo supervisorctl status abis-backend

# Nginx
sudo systemctl status nginx

# MySQL
sudo systemctl status mysql

# Disk space
df -h

# Memory usage
free -h
```

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 👥 Contributors

- **Muhammad** - Initial development

---

## 📞 Support

For issues, questions, or contributions:
- Create an issue on GitHub
- Email: your-email@example.com

---

## 🎉 Acknowledgments

- **Whisper** by OpenAI - Speech recognition
- **DeepFace** - Facial emotion detection
- **Sentence Transformers** - Semantic text analysis
- **FastAPI** - Modern web framework
- **React** - UI library

---

**Built with ❤️ for better hiring decisions**
