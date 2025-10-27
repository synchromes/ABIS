# 🚀 Quick Start Guide - ABIS

Get ABIS running in **15 minutes**!

## 📋 Prerequisites

- **Python 3.10+** installed
- **Node.js 18+** and npm installed
- **MySQL 8.0+** running
- **FFmpeg** installed

## ⚡ Quick Setup (Local Development)

### 1. Clone Repository

```bash
git clone https://github.com/synchromes/abis.git
cd abis
```

### 2. Backend Setup (5 minutes)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings
```

**Edit `.env`:**
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/abis_interview
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=http://localhost:3000
```

**Create database:**
```sql
CREATE DATABASE abis_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**Run migrations:**
```bash
python -m alembic upgrade head
```

**Create admin user:**
```bash
python create_admin.py
```

**Start backend:**
```bash
python run.py
```

Backend running at: `http://localhost:8000` ✅

### 3. Frontend Setup (5 minutes)

Open new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Create .env
cp .env.example .env
# Edit with: VITE_API_URL=http://localhost:8000/api

# Start dev server
npm run dev
```

Frontend running at: `http://localhost:5173` ✅

### 4. Login & Test

1. Open: `http://localhost:5173`
2. Login with admin credentials
3. Create your first interview!

---

## 🌐 Quick Deploy to VPS (30 minutes)

### One-Line Setup

```bash
# On fresh Ubuntu 20.04+ VPS
curl -sSL https://raw.githubusercontent.com/synchromes/abis/main/setup_vps.sh | sudo bash
```

The script will:
- ✅ Install all dependencies
- ✅ Setup MySQL database
- ✅ Configure Nginx
- ✅ Setup SSL certificate
- ✅ Deploy application

### Manual Deploy

```bash
# On your VPS
git clone https://github.com/synchromes/abis.git /var/www/abis
cd /var/www/abis
sudo ./setup_vps.sh
```

### Update Deployment

```bash
cd /var/www/abis
./deploy.sh
```

---

## 🔧 Common Commands

### Backend

```bash
# Start backend (dev)
python run.py

# Start backend (production)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000

# Run migrations
python -m alembic upgrade head

# Create admin
python create_admin.py
```

### Frontend

```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Database

```bash
# Backup
mysqldump -u root -p abis_interview > backup.sql

# Restore
mysql -u root -p abis_interview < backup.sql
```

---

## 📚 Next Steps

- Read full [README.md](README.md) for detailed documentation
- Visit [API Docs](http://localhost:8000/docs) for API reference
- Check [Troubleshooting](#troubleshooting) if you encounter issues

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check logs
tail -f backend.log

# Verify database connection
mysql -u root -p abis_interview

# Check Python version
python --version  # Should be 3.10+
```

### Frontend can't connect

```bash
# Verify backend is running
curl http://localhost:8000/docs

# Check VITE_API_URL in frontend/.env
cat frontend/.env
```

### Processing fails

```bash
# Check FFmpeg is installed
ffmpeg -version

# Check RAM availability
free -h  # Need 8GB+ for large-v2 model
```

---

## 🎉 All Set!

Your ABIS system is ready! Start creating interviews and let AI help you make better hiring decisions!

**Need help?**
- 📖 Full docs: [README.md](README.md)
- 🐛 Issues: [GitHub Issues](https://github.com/synchromes/abis/issues)
- 💬 Support: your-email@example.com
