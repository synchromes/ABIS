# ABIS Interview Assistant - Backend

AI-powered interview assistant system untuk seleksi Calon ASN dengan analisis perilaku real-time.

## Fitur Utama

### 1. AI Processing
- **Speech-to-Text**: Whisper model untuk transkrip Bahasa Indonesia
- **Facial Emotion Recognition**: Analisis ekspresi wajah real-time
- **Speech Emotion Recognition**: Deteksi emosi dari intonasi suara
- **NLP Analysis**: Analisis nilai BerAKHLAK menggunakan sentence transformers
- **Behavioral Scoring**: Scoring engine multi-dimensi

### 2. Real-time Features
- WebSocket untuk streaming video dan audio
- Live emotion detection dan transcript
- Real-time scoring dan indicators
- Dashboard monitoring untuk pewawancara

### 3. Security
- JWT Authentication
- AES256 encryption untuk rekaman
- Role-based access control (Admin, Interviewer, Viewer)
- On-premise deployment (no cloud)

### 4. Reporting
- PDF report generation
- JSON export
- Transkrip lengkap dengan analisis
- Grafik radar nilai BerAKHLAK

## Struktur Direktori

```
backend/
├── app/
│   ├── api/              # REST API endpoints
│   │   ├── auth.py       # Authentication
│   │   └── interviews.py # Interview management
│   ├── core/             # Core configuration
│   │   ├── config.py     # Settings
│   │   ├── database.py   # Database connection
│   │   └── security.py   # JWT & encryption
│   ├── models/           # SQLAlchemy models
│   │   ├── user.py
│   │   └── interview.py
│   ├── schemas/          # Pydantic schemas
│   │   ├── user.py
│   │   └── interview.py
│   ├── services/         # AI services
│   │   ├── speech_to_text.py
│   │   ├── facial_emotion.py
│   │   ├── speech_emotion.py
│   │   ├── nlp_analyzer.py
│   │   ├── behavioral_scoring.py
│   │   └── report_generator.py
│   ├── websocket/        # WebSocket handlers
│   │   └── interview_handler.py
│   └── main.py           # FastAPI application
├── ml_models/            # AI model files (download separately)
├── storage/              # File storage
│   ├── uploads/
│   ├── recordings/
│   └── reports/
├── requirements.txt
├── run.py
└── .env
```

## Instalasi

### 1. Prerequisites
- Python 3.9+
- MySQL 8.0+
- FFmpeg (untuk audio processing)

### 2. Setup Python Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Setup Database

```bash
# Login ke MySQL
mysql -u root -p

# Jalankan script SQL
source ../database/init.sql

# Atau import manual:
mysql -u root -p < ../database/init.sql
```

### 4. Configuration

Copy `.env.example` ke `.env` dan sesuaikan:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/abis_interview
SECRET_KEY=generate-random-secret-key-here
ENCRYPTION_KEY=generate-32-byte-key-here
```

Generate secret keys:
```python
import secrets
print(secrets.token_urlsafe(32))  # untuk SECRET_KEY
print(secrets.token_urlsafe(32))  # untuk ENCRYPTION_KEY
```

### 5. Download AI Models

Models akan di-download otomatis saat pertama kali dijalankan:
- Whisper: `base` model (~140MB)
- Sentence Transformers: `paraphrase-multilingual-MiniLM-L12-v2` (~420MB)
- FER: Pre-trained model (~5MB)

Atau download manual ke folder `ml_models/`

## Running the Application

### Development Mode

```bash
python run.py
```

Atau dengan uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Set DEBUG=False di .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Menggunakan Gunicorn (Production)

```bash
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Documentation

Setelah aplikasi berjalan, akses:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register user baru
- `POST /api/auth/login` - Login (form-data)
- `POST /api/auth/login/json` - Login (JSON)
- `GET /api/auth/me` - Get current user info

### Interviews
- `POST /api/interviews/` - Create interview
- `GET /api/interviews/` - List interviews
- `GET /api/interviews/{id}` - Get interview detail
- `PUT /api/interviews/{id}` - Update interview
- `POST /api/interviews/{id}/start` - Start interview
- `POST /api/interviews/{id}/complete` - Complete interview
- `PUT /api/interviews/{id}/scores` - Update scores
- `DELETE /api/interviews/{id}` - Delete interview

### WebSocket
- `WS /ws/interview/{id}` - Real-time interview processing

#### WebSocket Messages

**Client → Server:**

```json
// Video frame
{
  "type": "video_frame",
  "data": "base64_encoded_frame"
}

// Audio chunk
{
  "type": "audio_chunk",
  "data": "base64_encoded_audio"
}

// Save transcript
{
  "type": "save_transcript",
  "data": {
    "speaker": "Candidate",
    "text": "Transkrip...",
    "timestamp": 123.45,
    "confidence": 0.95
  }
}

// Get analysis
{
  "type": "get_analysis"
}
```

**Server → Client:**

```json
// Emotion update
{
  "type": "emotion_update",
  "data": {
    "emotion": "happy",
    "confidence": 0.85,
    "stability": 0.92,
    "all_emotions": { ... }
  }
}

// Transcript update
{
  "type": "transcript_update",
  "data": {
    "text": "...",
    "timestamp": 123.45,
    "berakhlak_scores": { ... },
    "coherence": 0.87
  }
}

// Analysis update
{
  "type": "analysis_update",
  "data": {
    "dimension_scores": { ... },
    "overall_scores": { ... }
  }
}
```

## Default Users

Setelah database di-setup:

**Admin:**
- Username: `admin`
- Password: `admin123`

**Interviewer:**
- Username: `interviewer1`
- Password: `interviewer123`

## Nilai BerAKHLAK

System menganalisis 7 dimensi nilai ASN:

1. **Berorientasi Pelayanan**: Fokus pada pelayanan publik
2. **Akuntabel**: Tanggung jawab dan transparansi
3. **Kompeten**: Keahlian dan profesionalisme
4. **Harmonis**: Kerjasama dan toleransi
5. **Loyal**: Komitmen dan dedikasi
6. **Adaptif**: Fleksibilitas dan inovasi
7. **Kolaboratif**: Kerja tim dan koordinasi

Setiap dimensi dinilai 0-5 berdasarkan:
- Analisis NLP dari transkrip (70%)
- Behavioral indicators: emotion stability, speech clarity, coherence (30%)

## Troubleshooting

### Error: "Module not found"
```bash
pip install -r requirements.txt
```

### Error: "Can't connect to MySQL"
- Pastikan MySQL service running
- Check DATABASE_URL di .env
- Test koneksi: `mysql -u root -p`

### Error: "CUDA not available"
- Sistem akan otomatis gunakan CPU
- Untuk GPU support, install torch dengan CUDA:
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Model download lambat
- Download manual dari Hugging Face
- Simpan di folder `ml_models/`
- Update path di `config.py`

## Performance Optimization

### 1. Model Optimization (ONNX)
```python
# Convert ke ONNX untuk inferensi lebih cepat
# Script akan ditambahkan di masa depan
```

### 2. Database Indexing
Sudah ada indexes pada:
- users.username, users.email
- interviews.status, interviews.interviewer_id
- transcript_entries.interview_id, transcript_entries.timestamp
- emotion_logs.interview_id, emotion_logs.timestamp

### 3. Caching
- Redis dapat ditambahkan untuk cache analysis results
- Session caching untuk AI models

## Security Best Practices

1. **Change Default Passwords**: Ganti password default users
2. **Strong Secret Keys**: Generate secure random keys
3. **HTTPS**: Deploy dengan SSL/TLS certificate
4. **Firewall**: Restrict access ke port 8000
5. **Regular Updates**: Update dependencies untuk security patches

## Development

### Running Tests
```bash
# Install pytest
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Formatting
```bash
pip install black isort
black app/
isort app/
```

## License

Proprietary - Internal use only

## Support

Untuk pertanyaan dan support, hubungi tim development.
