# 🎯 ABIS - Sistem Wawancara Berbasis AI

**ABIS** (Sistem Wawancara Berbasis AI) adalah sistem wawancara berbasis AI yang menggunakan teknologi canggih untuk menganalisis kandidat secara objektif dan komprehensif.

## 📋 Daftar Isi

- [Fitur](#-fitur)
- [Teknologi yang Digunakan](#-teknologi-yang-digunakan)
- [Persyaratan](#-persyaratan)
- [Instalasi (Pengembangan Lokal)](#-instalasi-pengembangan-lokal)
- [Deploy ke VPS Linux](#-deploy-ke-vps-linux)
- [Konfigurasi](#-konfigurasi)
- [Panduan Penggunaan](#-panduan-penggunaan)
- [Dokumentasi API](#-dokumentasi-api)
- [Pemecahan Masalah](#-pemecahan-masalah)

---

## 🎨 Fitur

### Fitur Utama
- ✅ **Live Interview Recording** - Merekam langsung menggunakan webcam & audio
- ✅ **AI Transkripsi** - Model Whisper large-v2 untuk akurasi speech-to-text
- ✅ **Deteksi Emosi Ganda** - Sentimen/Emosi Wajah (DeepFace) + Suara
- ✅ **Analisis Semantik Hybrid** - Analisis semantik berdasarkan hasil jawaban
- ✅ **Indikator Kustom** - Kustomisasi indikator penilaian
- ✅ **Penilaian AI** - Memberikan skor otomatis beserta alasannya
- ✅ **Skor Manual** - Pewawancara bisa memasukkan penilaian
- ✅ **Perhitungan Skor Dinamis** - Perhitungan bobot skor antara AI dan Pewawancara

### Fitur Lanjutan
- ✅ **Dashboard Analitik**
- ✅ **Interview Transcript Viewer** - Transcript penuh calon pegawai
- ✅ **Real-time Audio Visualizer** - Visualisasi gelombang suara ketika wawancara berlangsung
- ✅ **Timer & Stopwatch** - Timestamp ketika wawancara berlangsung
- ✅ **Grafik Emosi** - Grafik sentimen emosi wajah dan suara

---

## 🛠 Teknologi yang Digunakan

### Backend
- **Framework:** FastAPI (Python 3.10+)
- **Database:** MySQL 8.0+
- **ORM:** SQLAlchemy 2.0
- **Autentikasi:** JWT (python-jose)
- **Model AI:**
  - Whisper Large-v2 (faster-whisper)
  - DeepFace (deteksi emosi)
  - Sentence Transformers (analisis semantik)

### Frontend
- **Framework:** React 18 + Vite
- **Manajemen State:** Zustand
- **Styling:** Tailwind CSS
- **Grafik:** Recharts
- **Routing:** React Router v6
- **HTTP Client:** Axios

---

## 📦 Persyaratan

### Persyaratan Sistem
- **OS:** Windows 10+, Ubuntu 20.04+, atau macOS 12+
- **RAM:** Minimum 8GB (16GB direkomendasikan untuk proses AI)
- **Storage:** 10GB ruang bebas (untuk model AI)
- **CPU:** Prosesor multi-core direkomendasikan

### Persyaratan Software
- **Python:** 3.13+ (development di 3.13.9)
- **Node.js:** 18.x atau 20.x
- **MySQL:** 8.0+
- **FFmpeg:** Dibutuhkan untuk pemrosesan audio

---

## 🚀 Instalasi (Pengembangan Lokal)

### 1. Clone Repository

```bash
git clone https://github.com/synchromes/abis.git
cd abis
```

### 2. Setup Backend

#### Install Dependensi Python

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

**Windows (menggunakan Chocolatey):**
```bash
choco install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS (menggunakan Homebrew):**
```bash
brew install ffmpeg
```

#### Setup Database

1. Buat database MySQL:
```sql
CREATE DATABASE abis_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Buat file `.env` di `backend/`:
```env
# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/abis_interview

# Autentikasi JWT
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Upload File
UPLOAD_DIR=uploads
MAX_FILE_SIZE=104857600

# Model AI
WHISPER_MODEL=large-v2
WHISPER_DEVICE=cpu
DEEPFACE_BACKEND=opencv
```

3. Jalankan migrasi:
```bash
# Apply migrations
python -m alembic upgrade head
```

4. Buat user awal:
```bash
python create_admin.py
```

#### Jalankan Backend Server

```bash
# Development
python run.py

# Produksi (menggunakan Gunicorn)
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

Backend akan berjalan di: `http://localhost:8000`

### 3. Setup Frontend

```bash
cd frontend

# Install dependencies
npm install

# Buat file .env
cp .env.example .env
```

Edit `.env`:
```env
VITE_API_URL=http://localhost:8000/api
```

#### Jalankan Frontend Dev Server

```bash
# Development
npm run dev

# Build untuk produksi
npm run build

# Preview build produksi
npm run preview
```

Frontend akan berjalan di: `http://localhost:5173` atau `http://localhost:3000`

---

## 🌐 Deploy ke VPS Linux

### Prasyarat

- VPS Ubuntu 20.04+
- Akses root atau sudo
- Minimum 4GB RAM, 2 CPU core

### 1. Setup Server Awal

```bash
# Update sistem
sudo apt update && sudo apt upgrade -y

# Install paket yang dibutuhkan
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
# Amankan instalasi MySQL
sudo mysql_secure_installation

# Buat database
sudo mysql -u root -p
```

```sql
CREATE DATABASE abis_interview CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'abis_user'@'localhost' IDENTIFIED BY 'your_strong_password';
GRANT ALL PRIVILEGES ON abis_interview.* TO 'abis_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 4. Clone dan Setup Aplikasi

```bash
# Buat direktori aplikasi
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

# Buat .env produksi
nano .env
```

`.env` produksi:
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
# Buat direktori uploads
mkdir -p /var/www/abis/uploads
chmod 755 /var/www/abis/uploads

# Jalankan migrasi
python -m alembic upgrade head

# Buat admin user
python create_admin.py
```

### 5. Setup Frontend

```bash
cd /var/www/abis/frontend

# Install dependencies
npm install

# Buat .env produksi
nano .env
```

```env
VITE_API_URL=https://yourdomain.com/api
```

```bash
# Build untuk produksi
npm run build
```

### 6. Konfigurasi Supervisor (Backend)

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

### 7. Konfigurasi Nginx

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
# Aktifkan site
sudo ln -s /etc/nginx/sites-available/abis /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 8. Setup SSL (Opsional tapi Disarankan)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Dapatkan sertifikat SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal sudah diatur otomatis
```

### 9. Setup Firewall

```bash
sudo ufw allow 'Nginx Full'
sudo ufw allow OpenSSH
sudo ufw enable
```

### 10. Verifikasi Deploy

```bash
# Cek status backend
sudo supervisorctl status abis-backend

# Cek log backend
sudo tail -f /var/log/abis-backend.log

# Cek Nginx
sudo systemctl status nginx
```

Kunjungi: `https://yourdomain.com`

---

## ⚙️ Konfigurasi

### Konfigurasi Backend

Semua konfigurasi backend ada di file `.env`:

| Variabel | Deskripsi | Default |
|----------|-----------|---------|
| `DATABASE_URL` | String koneksi MySQL | - |
| `SECRET_KEY` | Kunci rahasia JWT | - |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Kadaluarsa token | 30 |
| `CORS_ORIGINS` | Origin yang diizinkan (pisahkan koma) | * |
| `UPLOAD_DIR` | Path direktori upload | uploads |
| `MAX_FILE_SIZE` | Maksimal ukuran file (byte) | 100MB |
| `WHISPER_MODEL` | Ukuran model Whisper | large-v2 |
| `WHISPER_DEVICE` | Device pemrosesan | cpu |
| `DEEPFACE_BACKEND` | Backend deteksi wajah | opencv |

### Konfigurasi Frontend

Konfigurasi frontend di file `.env`:

| Variabel | Deskripsi | Default |
|----------|-----------|---------|
| `VITE_API_URL` | URL API backend | http://localhost:8000/api |

---

## 📖 Panduan Penggunaan

### 1. Login

Kredensial default:
- **Username:** admin
- **Password:** admin123

### 2. Membuat Interview

1. Pergi ke halaman **Interviews**
2. Klik **"+ Buat Interview Baru"**
3. Isi detail calon pegawai:
   - Nama
   - Email
   - Nomor Identitas
   - Posisi
   - Jadwal
4. Klik **"Lanjut"**

### 3. Setup indikator penilaian

1. Tambahkan indikator dengan isi:
   - Nama indikator (misal, "Kepemimpinan")
   - Deskripsi (misal, "Kemampuan memimpin tim dan mengambil keputusan")
   - Bobot (1-10, tinggi = semakin penting)

### 4. Memulai Wawancara

1. Klik **"Mulai Wawancara"**
2. Berikan izin kamera dan mikrofon
3. Rekaman wawancara dimulai dengan:
   - Live video preview
   - Visualisasi gelombang suara
   - Timer/stopwatch
4. Klik **"Selesai"** saat wawancara selesai

### 5. Proses Wawancara

1. Setelah rekaman, klik **"Process Interview"**
2. AI akan:
   - Mentranskrip audio (menggunakan Whisper)
   - Deteksi emosi (wajah + suara)
   - Analisis jawaban sesuai indikator
   - Menghasilkan skor dan rekomendasi
3. Proses membutuhkan waktu ~2-5 menit tergantung panjang wawancara

### 6. Review Penilaian

1. Pergi ke tab **"Assessment"**
2. Review:
   - Skor AI per indikator
   - Bukti dari transcript
   - Alasan penilaian
   - Grafik emosi
3. Bisa menambah **Skor Manual** untuk override AI

### 7. Melihat Dashboard

- **Dashboard Overview** menampilkan:
  - Total wawancara
  - Tingkat penyelesaian
  - Rata-rata skor
  - Persentase sukses AI
  - Grafik distribusi skor
  - Top 5 kandidat
  - Quick actions

---

## 📚 Dokumentasi API

### Akses API Docs

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Endpoint Utama

#### Autentikasi
- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Registrasi pengguna baru
- `GET /api/auth/me` - Mendapatkan user saat ini

#### Interview
- `GET /api/interviews/` - List interview (dengan pagination)
- `POST /api/interviews/` - Buat interview
- `GET /api/interviews/{id}` - Detail interview
- `POST /api/interviews/{id}/start` - Mulai interview
- `POST /api/interviews/{id}/complete` - Selesaikan interview
- `POST /api/interviews/{id}/process` - Proses interview dengan AI
- `DELETE /api/interviews/{id}` - Hapus interview

#### Dashboard & Analitik
- `GET /api/interviews/dashboard/statistics` - Statistik dashboard
- `GET /api/interviews/compare?interview_ids=1,2` - Bandingkan kandidat
- `GET /api/interviews/{id}/recommendations` - Rekomendasi AI
- `GET /api/interviews/{id}/transcript` - Transcript penuh

#### Indikator
- `GET /api/interviews/{id}/indicators` - Indikator interview
- `POST /api/interviews/{id}/indicators` - Tambah indikator
- `DELETE /api/interviews/{id}/indicators/{indicator_id}` - Hapus indikator

#### Penilaian
- `GET /api/interviews/{id}/assessment` - Hasil penilaian
- `PUT /api/interviews/{id}/manual-scores` - Update skor manual
- `POST /api/interviews/recalculate-scores` - Hitung ulang semua skor

---

## 🔧 Pemecahan Masalah

### Masalah Umum

#### 1. Backend tidak bisa berjalan

**Error:** `ModuleNotFoundError: No module named 'faster_whisper'`

**Solusi:**
```bash
cd backend
source venv/bin/activate  # atau venv\Scripts\activate di Windows
pip install -r requirements.txt
```

#### 2. Error koneksi database

**Error:** `Can't connect to MySQL server`

**Solusi:**
- Pastikan MySQL berjalan: `sudo systemctl status mysql`
- Cek kredensial di `.env`
- Tes koneksi: `mysql -u abis_user -p abis_interview`

#### 3. Frontend tidak bisa konek ke backend

**Error:** `Network Error` atau `CORS Error`

**Solusi:**
- Pastikan backend berjalan: `http://localhost:8000/docs`
- Cek `VITE_API_URL` di frontend `.env`
- Cek `CORS_ORIGINS` di backend `.env`

#### 4. Proses Interview gagal

**Error:** `Whisper model not found` atau `Processing failed`

**Solusi:**
- Pastikan FFmpeg terinstall: `ffmpeg -version`
- Cek RAM cukup (8GB+ untuk model large-v2)
- Cek log: `sudo tail -f /var/log/abis-backend.log`

#### 5. Upload gagal

**Error:** `413 Request Entity Too Large`

**Solusi:**
- Naikkan limit Nginx:
```nginx
client_max_body_size 100M;
```
- Restart Nginx: `sudo systemctl restart nginx`

#### 6. Skor selalu 0

**Solusi:**
```bash
# Gunakan endpoint recalculate lewat Swagger UI
# Atau proses ulang interview
```

---

## 🔄 Maintenance

### Update Aplikasi

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

### Monitor Log

```bash
# Log backend
sudo tail -f /var/log/abis-backend.log

# Log akses Nginx
sudo tail -f /var/log/nginx/access.log

# Log error Nginx
sudo tail -f /var/log/nginx/error.log
```

### Cek Status

```bash
# Backend
sudo supervisorctl status abis-backend

# Nginx
sudo systemctl status nginx

# MySQL
sudo systemctl status mysql

# Disk space
df -h

# Penggunaan memori
free -h
```

---

## 📄 Lisensi

Proyek ini merupakan prototype untuk ASN Digital AI Hackaton

---

## 👥 Tim

- **Muchamad Ramadhan Surya**
- **Ilham Sidik Saksena**
- **Yonita Anggrearia**

---

## TVRI Kalimantan Barat

---
