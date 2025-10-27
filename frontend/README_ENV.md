# Environment Configuration

Frontend menggunakan Vite environment variables.

## File .env

File `.env` sudah dibuat dengan konfigurasi default untuk development.

### Default Configuration

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_APP_NAME=ABIS Interview Assistant
VITE_APP_VERSION=1.0.0
VITE_ENV=development
```

## Cara Menggunakan

Environment variables otomatis di-load oleh Vite.

Akses di kode dengan `import.meta.env`:

```javascript
// Langsung akses
const apiUrl = import.meta.env.VITE_API_BASE_URL

// Atau gunakan config helper
import config from './config'
const apiUrl = config.apiBaseUrl
```

## Production Deployment

Untuk production, buat file `.env.production`:

```env
VITE_API_BASE_URL=https://your-production-domain.com
VITE_WS_BASE_URL=wss://your-production-domain.com
VITE_APP_NAME=ABIS Interview Assistant
VITE_APP_VERSION=1.0.0
VITE_ENV=production
```

## Environment Files

- `.env` - Default untuk semua environment
- `.env.local` - Local overrides (not committed)
- `.env.development` - Development specific
- `.env.production` - Production specific

## Notes

⚠️ **IMPORTANT**: Vite hanya expose variables yang diawali dengan `VITE_`

✅ Correct: `VITE_API_URL`  
❌ Wrong: `API_URL` (tidak akan terexpose)

📝 Setelah mengubah `.env`, restart dev server:
```bash
# Stop server (Ctrl+C)
# Start lagi
npm run dev
```

## Backend URL Configuration

Saat ini frontend dikonfigurasi untuk connect ke:
- **API**: http://localhost:8000/api
- **WebSocket**: ws://localhost:8000/ws

Jika backend berjalan di port atau host lain, update `.env`:

```env
VITE_API_BASE_URL=http://localhost:9000
VITE_WS_BASE_URL=ws://localhost:9000
```

## Testing Different Backends

Untuk test dengan backend yang berbeda tanpa edit .env:

```bash
# Option 1: Override saat start
VITE_API_BASE_URL=http://192.168.1.100:8000 npm run dev

# Option 2: Buat .env.local
echo "VITE_API_BASE_URL=http://192.168.1.100:8000" > .env.local
npm run dev
```

## Troubleshooting

### Frontend tidak connect ke backend

1. Check `.env` values correct
2. Check backend running di URL yang sama
3. Restart dev server setelah edit .env
4. Check browser console untuk error

### CORS Error

Jika error CORS, pastikan backend `.env` include frontend URL:

```env
# Di backend/.env
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### WebSocket Connection Failed

1. Check backend WebSocket endpoint available
2. Check `VITE_WS_BASE_URL` protocol (`ws://` not `http://`)
3. For HTTPS frontend, use `wss://` for WebSocket
