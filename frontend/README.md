# ABIS Interview Assistant - Frontend

Dashboard web untuk AI Interview Assistant System menggunakan React + Vite.

## Fitur

### 1. Authentication
- Login system dengan JWT
- Role-based access control
- Session management dengan Zustand

### 2. Dashboard
- Statistik wawancara (total, terjadwal, berlangsung, selesai)
- Daftar wawancara terbaru
- Quick actions

### 3. Interview Management
- CRUD wawancara
- Filter dan search
- Status tracking

### 4. Live Interview Session
- Real-time video capture dari webcam
- Audio streaming ke backend
- Live emotion detection
- Live transcript dengan Speech-to-Text
- Real-time indicators:
  - Stabilitas emosi
  - Kejelasan komunikasi
  - Koherensi jawaban
- Grafik radar nilai BerAKHLAK real-time
- Recording controls (start/stop)

### 5. Interview Report
- Laporan lengkap pasca-wawancara
- Grafik radar nilai BerAKHLAK
- Indikator perilaku
- Transkrip lengkap
- Input skor manual pewawancara
- Export PDF & JSON
- Rekomendasi akhir

## Tech Stack

- **React 18** - UI library
- **Vite** - Build tool & dev server
- **TailwindCSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **Zustand** - State management
- **WebSocket** - Real-time communication
- **React Webcam** - Webcam capture
- **Recharts** - Data visualization
- **React Hot Toast** - Notifications
- **Lucide React** - Icons
- **date-fns** - Date formatting

## Instalasi

### Prerequisites
- Node.js 18+ 
- npm atau yarn

### Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables (optional)
# Update API URL jika perlu

# Start development server
npm run dev
```

Server akan berjalan di `http://localhost:3000`

## Development

### Project Structure

```
src/
├── components/          # Reusable components
│   ├── Layout.jsx
│   ├── RadarChart.jsx
│   ├── EmotionIndicator.jsx
│   └── TranscriptPanel.jsx
├── pages/              # Page components
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── InterviewList.jsx
│   ├── InterviewSession.jsx
│   ├── InterviewReport.jsx
│   └── NotFound.jsx
├── services/           # API & WebSocket services
│   ├── api.js
│   └── websocket.js
├── stores/             # Zustand stores
│   └── authStore.js
├── App.jsx            # Main app component
├── main.jsx           # Entry point
└── index.css          # Global styles
```

### API Configuration

Backend API URL dikonfigurasi via Vite proxy di `vite.config.js`:

```js
server: {
  proxy: {
    '/api': 'http://localhost:8000',
    '/ws': {
      target: 'ws://localhost:8000',
      ws: true
    }
  }
}
```

### WebSocket Integration

WebSocket service (`services/websocket.js`) menangani:
- Connection management
- Message routing
- Video frame streaming
- Audio chunk streaming
- Real-time updates (emotion, transcript, analysis)
- Auto-reconnection

### State Management

**Auth Store** (`stores/authStore.js`):
- User authentication state
- Token management
- Persistent storage (localStorage)

### Styling

Menggunakan TailwindCSS dengan custom components:
- `.btn`, `.btn-primary`, `.btn-secondary`, `.btn-danger`
- `.card`
- `.input`
- `.badge`, `.badge-success`, `.badge-warning`, etc.

## Available Scripts

```bash
# Development server dengan hot reload
npm run dev

# Build untuk production
npm run build

# Preview production build
npm run preview

# Linting
npm run lint
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Requirements:**
- WebSocket support
- getUserMedia API (webcam/mic access)
- MediaRecorder API
- ES2020+ support

## Features Deep Dive

### Real-time Interview Session

1. **Video Capture**
   - Menggunakan `react-webcam`
   - Frame capture setiap 200ms
   - Base64 encoding
   - Streaming via WebSocket

2. **Audio Capture**
   - Web Audio API
   - AudioContext dengan sample rate 16kHz
   - ScriptProcessor untuk chunking
   - Int16 PCM encoding

3. **Real-time Analysis Display**
   - Emotion indicator dengan confidence level
   - Behavioral metrics (bars)
   - Radar chart untuk 7 dimensi BerAKHLAK
   - Live transcript dengan scroll

4. **WebSocket Messages**

**Client → Server:**
```json
{
  "type": "video_frame",
  "data": "base64_frame_data"
}

{
  "type": "audio_chunk",
  "data": "base64_audio_data"
}
```

**Server → Client:**
```json
{
  "type": "emotion_update",
  "data": {
    "emotion": "happy",
    "confidence": 0.85,
    "stability": 0.92
  }
}

{
  "type": "transcript_update",
  "data": {
    "text": "...",
    "berakhlak_scores": {...},
    "coherence": 0.87
  }
}
```

### Interview Report

1. **Data Visualization**
   - Radar chart menggunakan Recharts
   - Progress bars untuk metrics
   - Color-coded recommendations

2. **Manual Scoring**
   - Input fields untuk 7 dimensi BerAKHLAK
   - Auto-calculate average dengan AI score
   - Save to backend

3. **Export Options**
   - PDF generation (via backend API)
   - JSON export untuk data processing

## Troubleshooting

### Webcam tidak berfungsi
- Pastikan browser memiliki akses webcam
- Check HTTPS (beberapa browser require HTTPS untuk getUserMedia)
- Periksa console untuk error

### WebSocket disconnected
- Pastikan backend running di port 8000
- Check network tab untuk WebSocket connection
- Auto-reconnection akan retry 5x dengan backoff

### Build gagal
```bash
# Clear cache
rm -rf node_modules
npm install

# Clear Vite cache
rm -rf .vite

# Rebuild
npm run build
```

### CORS errors
- Pastikan backend CORS config include frontend URL
- Check `CORS_ORIGINS` di backend `.env`

## Performance Tips

1. **Optimize video frame rate**
   - Default: 5 FPS (200ms interval)
   - Adjustable di `InterviewSession.jsx`

2. **Audio chunk size**
   - Default: 4096 samples
   - Trade-off: latency vs processing load

3. **Transcript scroll**
   - Auto-scroll ke bottom
   - Limit displayed entries untuk performance

4. **Component memoization**
   - Use React.memo untuk expensive components
   - useMemo untuk computed values

## Security

1. **Token Management**
   - JWT stored in localStorage
   - Auto-attached to API requests
   - Auto-logout on 401 response

2. **WebSocket Security**
   - Interview ID validation
   - Connection per session
   - Cleanup on disconnect

3. **Input Sanitization**
   - Form validation
   - XSS prevention (React default)

## Production Deployment

### Build

```bash
npm run build
```

Output: `dist/` folder

### Deploy Options

1. **Static Hosting** (Vercel, Netlify, etc.)
```bash
# Deploy dist folder
# Configure redirects untuk SPA routing
```

2. **Nginx**
```nginx
server {
  listen 80;
  server_name your-domain.com;
  
  root /var/www/abis/frontend/dist;
  index index.html;
  
  location / {
    try_files $uri $uri/ /index.html;
  }
  
  location /api {
    proxy_pass http://localhost:8000;
  }
  
  location /ws {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
  }
}
```

3. **Docker**
```dockerfile
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Future Enhancements

- [ ] Multi-language support (i18n)
- [ ] Dark mode
- [ ] Advanced analytics dashboard
- [ ] Batch interview processing
- [ ] Interview scheduling with calendar
- [ ] Email notifications
- [ ] Advanced report customization
- [ ] Interview templates
- [ ] Candidate self-assessment
- [ ] Video playback & review

## License

Proprietary - Internal use only

## Support

Untuk bug reports dan feature requests, hubungi tim development.
