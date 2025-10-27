import { useEffect, useState, useRef } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import Webcam from 'react-webcam'
import api from '../services/api'
import ws from '../services/websocket'
import toast from 'react-hot-toast'
import { 
  Video, VideoOff, Mic, MicOff, Play, Square, 
  Activity, MessageSquare, BarChart3, CheckCircle2, ExternalLink,
  Clock, User, Briefcase, Calendar
} from 'lucide-react'
import EmotionIndicator from '../components/EmotionIndicator'

export default function InterviewSession() {
  const { id } = useParams()
  const navigate = useNavigate()
  const webcamRef = useRef(null)
  const mediaRecorderRef = useRef(null)
  const audioContextRef = useRef(null)

  const [interview, setInterview] = useState(null)
  const [indicators, setIndicators] = useState([])
  const [isRecording, setIsRecording] = useState(false)
  const [videoEnabled, setVideoEnabled] = useState(true)
  const [audioEnabled, setAudioEnabled] = useState(true)
  const [loading, setLoading] = useState(true)
  
  // Use refs to avoid closure issues in intervals
  const isRecordingRef = useRef(false)
  const videoEnabledRef = useRef(true)
  const audioEnabledRef = useRef(true)

  const [currentEmotion, setCurrentEmotion] = useState({ emotion: 'neutral', confidence: 0 })
  const [emotionStability, setEmotionStability] = useState(0.8)
  
  // Timer for recording duration
  const [recordingTime, setRecordingTime] = useState(0)
  const timerIntervalRef = useRef(null)
  
  // Audio visualizer
  const audioVisualizerRef = useRef(null)
  const animationFrameRef = useRef(null)
  const analyserRef = useRef(null)

  useEffect(() => {
    loadInterview()
    loadIndicators()
    return () => {
      if (isRecording) {
        stopRecording()
      }
      ws.disconnect()
    }
  }, [id])

  const loadInterview = async () => {
    try {
      const response = await api.get(`/interviews/${id}`)
      setInterview(response.data)
      setLoading(false)
    } catch (error) {
      toast.error('Gagal memuat data wawancara')
      navigate('/interviews')
    }
  }

  const loadIndicators = async () => {
    try {
      const response = await api.get(`/interviews/${id}/indicators`)
      setIndicators(response.data)
    } catch (error) {
      console.error('Failed to load indicators:', error)
    }
  }

  const startRecording = async () => {
    try {
      console.log('[Session] Starting interview recording...')
      
      // Start interview (set started_at timestamp)
      console.log('[Session] Marking interview as started...')
      await api.post(`/interviews/${id}/start`)
      console.log('[Session] Interview started timestamp recorded')
      
      await ws.connect(id)
      console.log('[Session] WebSocket connected')

      ws.on('emotion_update', (data) => {
        console.log('[WS] Emotion update:', data)
        setCurrentEmotion({
          emotion: data.emotion,
          confidence: data.confidence
        })
        setEmotionStability(data.stability)
      })

      setIsRecording(true)
      isRecordingRef.current = true
      
      // Start timer
      setRecordingTime(0)
      timerIntervalRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)
      
      console.log('[Session] Starting video and audio capture...')
      startVideoCapture()
      await startAudioCapture()
      console.log('[Session] Captures started')
      
      console.log('[Session] Recording fully started')
    } catch (error) {
      console.error('[Session] Error starting recording:', error)
      toast.error('Gagal memulai rekaman')
    }
  }

  const stopRecording = async () => {
    try {
      console.log('[Session] Stopping recording...')
      
      setIsRecording(false)
      isRecordingRef.current = false
      
      // Stop timer
      if (timerIntervalRef.current) {
        clearInterval(timerIntervalRef.current)
        timerIntervalRef.current = null
      }
      
      // Stop audio visualizer
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
        animationFrameRef.current = null
      }
      
      if (window.videoIntervalId) {
        clearInterval(window.videoIntervalId)
        window.videoIntervalId = null
        console.log('[Video] Interval cleared')
      }
      
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop()
      }
      if (audioContextRef.current) {
        audioContextRef.current.close()
      }

      // Get final analysis and disconnect websocket
      console.log('[Session] Getting final analysis...')
      ws.getAnalysis()
      
      // Wait a bit for final messages to be processed
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Disconnect websocket (this will save audio_file_path to DB)
      console.log('[Session] Disconnecting websocket...')
      ws.disconnect()
      console.log('[Session] Websocket disconnected')

      // Complete interview
      console.log('[Session] Completing interview...')
      await api.post(`/interviews/${id}/complete`)
      console.log('[Session] Interview completed')
      
      toast.success('Wawancara selesai! Memulai AI processing...')
      
      // Wait a bit to ensure audio_file_path is saved by websocket disconnect handler
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Auto-trigger AI processing (async, don't wait)
      console.log('[Session] Starting AI processing...')
      api.post(`/interviews/${id}/process`)
        .then(() => {
          console.log('[Session] AI processing started successfully')
          toast.success('AI processing dimulai!')
        })
        .catch(processError => {
          console.error('[Session] Failed to start processing:', processError)
          toast.error('Gagal memulai AI processing, bisa diproses manual nanti')
        })
      
      // Redirect to report page after processing starts
      console.log('[Session] Redirecting to report page...')
      setTimeout(() => {
        console.log('[Session] Navigating to:', `/interview/${id}/report`)
        navigate(`/interview/${id}/report`)
      }, 500)
    } catch (error) {
      console.error('[Session] Error stopping recording:', error)
      toast.error('Gagal menghentikan rekaman')
    }
  }

  const startVideoCapture = () => {
    console.log('[Video] Starting video capture...')
    
    const videoInterval = setInterval(() => {
      if (!isRecordingRef.current || !videoEnabledRef.current || !webcamRef.current) {
        return
      }
      
      const imageSrc = webcamRef.current.getScreenshot()
      if (imageSrc) {
        ws.sendVideoFrame(imageSrc)
      }
    }, 200)

    window.videoIntervalId = videoInterval
  }

  const startAudioCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        audio: {
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false,
          sampleRate: 16000
        } 
      })
      
      const audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: 16000
      })
      audioContextRef.current = audioContext
      
      const source = audioContext.createMediaStreamSource(stream)
      const processor = audioContext.createScriptProcessor(4096, 1, 1)
      
      // Create analyser for visualization
      const analyser = audioContext.createAnalyser()
      analyser.fftSize = 2048
      analyser.smoothingTimeConstant = 0.8
      analyserRef.current = analyser
      
      source.connect(analyser)
      source.connect(processor)
      processor.connect(audioContext.destination)
      
      // Start visualization
      drawAudioVisualizer()
      
      processor.onaudioprocess = (e) => {
        if (!isRecordingRef.current || !audioEnabledRef.current) {
          return
        }
        
        const inputData = e.inputBuffer.getChannelData(0)
        const max = Math.max(...inputData.map(Math.abs))
        
        if (max > 0.01) {
          const int16Data = new Int16Array(inputData.length)
          for (let i = 0; i < inputData.length; i++) {
            int16Data[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32767))
          }
          
          const base64Audio = btoa(
            String.fromCharCode.apply(null, new Uint8Array(int16Data.buffer))
          )
          
          ws.sendAudioChunk(base64Audio)
        }
      }
    } catch (error) {
      console.error('[Audio] Error capturing audio:', error)
      toast.error('Gagal mengakses mikrofon')
    }
  }

  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60
    
    if (hrs > 0) {
      return `${hrs.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const drawAudioVisualizer = () => {
    if (!audioVisualizerRef.current || !analyserRef.current) return
    
    const canvas = audioVisualizerRef.current
    const canvasCtx = canvas.getContext('2d')
    const analyser = analyserRef.current
    
    const bufferLength = analyser.frequencyBinCount
    const dataArray = new Uint8Array(bufferLength)
    
    const draw = () => {
      if (!isRecordingRef.current) return
      
      animationFrameRef.current = requestAnimationFrame(draw)
      
      analyser.getByteTimeDomainData(dataArray)
      
      canvasCtx.fillStyle = '#f3f4f6'
      canvasCtx.fillRect(0, 0, canvas.width, canvas.height)
      
      canvasCtx.lineWidth = 2
      canvasCtx.strokeStyle = '#3b82f6'
      canvasCtx.beginPath()
      
      const sliceWidth = canvas.width / bufferLength
      let x = 0
      
      for (let i = 0; i < bufferLength; i++) {
        const v = dataArray[i] / 128.0
        const y = (v * canvas.height) / 2
        
        if (i === 0) {
          canvasCtx.moveTo(x, y)
        } else {
          canvasCtx.lineTo(x, y)
        }
        
        x += sliceWidth
      }
      
      canvasCtx.lineTo(canvas.width, canvas.height / 2)
      canvasCtx.stroke()
    }
    
    draw()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const formatDate = (dateString) => {
    if (!dateString) return '-'
    return new Date(dateString).toLocaleString('id-ID', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatDuration = (seconds) => {
    if (!seconds) return '-'
    const minutes = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${minutes} menit ${secs} detik`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{interview.candidate_name}</h1>
            <p className="text-gray-600">{interview.position}</p>
          </div>
          <div className="flex items-center space-x-4">
            {interview.status === 'completed' ? (
              <div className="flex items-center space-x-2">
                <CheckCircle2 size={20} className="text-green-600" />
                <span className="text-green-600 font-medium">Wawancara Selesai</span>
              </div>
            ) : (
              <>
                {isRecording && (
                  <div className="flex items-center space-x-2 text-red-600">
                    <div className="w-3 h-3 bg-red-600 rounded-full animate-pulse"></div>
                    <span className="font-medium">RECORDING</span>
                  </div>
                )}
                {!isRecording ? (
                  <button onClick={startRecording} className="btn btn-primary flex items-center space-x-2">
                    <Play size={20} />
                    <span>Mulai Wawancara</span>
                  </button>
                ) : (
                  <button onClick={stopRecording} className="btn btn-danger flex items-center space-x-2">
                    <Square size={20} />
                    <span>Selesai</span>
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {interview.status === 'completed' ? (
          /* Completed Interview View */
          <div className="space-y-6">
            {/* Interview Info */}
            <div className="card">
              <h2 className="text-lg font-bold mb-4">Informasi Wawancara</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-start space-x-3">
                  <User size={20} className="text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Kandidat</p>
                    <p className="font-medium">{interview.candidate_name}</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Briefcase size={20} className="text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Posisi</p>
                    <p className="font-medium">{interview.position}</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Calendar size={20} className="text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Dimulai</p>
                    <p className="font-medium">{formatDate(interview.started_at)}</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <Clock size={20} className="text-gray-400 mt-1" />
                  <div>
                    <p className="text-sm text-gray-600">Durasi</p>
                    <p className="font-medium">{formatDuration(interview.duration_seconds)}</p>
                  </div>
                </div>
              </div>
            </div>

            {/* Custom Indicators */}
            {indicators.length > 0 && (
              <div className="card">
                <h2 className="text-lg font-bold mb-4">Custom Indicators</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {indicators.map((indicator) => (
                    <div key={indicator.id} className="p-4 bg-gray-50 rounded-lg border">
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-semibold text-gray-900">{indicator.name}</h3>
                        <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                          Weight: {indicator.weight}x
                        </span>
                      </div>
                      <p className="text-sm text-gray-600">{indicator.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Processing Status & Actions */}
            <div className="card">
              <h2 className="text-lg font-bold mb-4">Status & Aksi</h2>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600 mb-2">Status Processing:</p>
                  {interview.processing_status === 'completed' ? (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                      <CheckCircle2 size={16} className="mr-2" />
                      Sudah Diproses
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                      Belum Diproses - Klik tombol "Process" di halaman Interview List
                    </span>
                  )}
                </div>
                
                <div className="flex flex-wrap gap-3">
                  {interview.processing_status === 'completed' && (
                    <Link
                      to={`/interview/${id}/assessment`}
                      className="btn btn-primary flex items-center space-x-2"
                    >
                      <BarChart3 size={18} />
                      <span>Lihat Assessment</span>
                      <ExternalLink size={16} />
                    </Link>
                  )}
                  <Link
                    to={`/interview/${id}/report`}
                    className="btn btn-secondary flex items-center space-x-2"
                  >
                    <MessageSquare size={18} />
                    <span>Lihat Laporan</span>
                    <ExternalLink size={16} />
                  </Link>
                  <button
                    onClick={() => navigate('/interviews')}
                    className="btn btn-outline"
                  >
                    Kembali ke Daftar
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Live Recording View */
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Video Section */}
            <div className="lg:col-span-2 space-y-6">
              {/* Timer & Audio Visualizer */}
              {isRecording && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Recording Timer */}
                  <div className="card bg-gradient-to-r from-red-50 to-orange-50 border-red-200">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <div className="w-4 h-4 bg-red-600 rounded-full animate-pulse"></div>
                        <div>
                          <p className="text-sm text-gray-600 font-medium">Durasi Rekaman</p>
                          <p className="text-3xl font-bold text-gray-900 font-mono">{formatTime(recordingTime)}</p>
                        </div>
                      </div>
                      <Clock size={32} className="text-red-500 opacity-50" />
                    </div>
                  </div>

                  {/* Audio Visualizer */}
                  <div className="card bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <p className="text-sm text-gray-600 font-medium">Live Audio</p>
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                          <span className="text-xs text-green-600 font-medium">Active</span>
                        </div>
                      </div>
                      <canvas
                        ref={audioVisualizerRef}
                        width="320"
                        height="60"
                        className="w-full rounded-lg border border-gray-200"
                        style={{ height: '60px' }}
                      />
                      <p className="text-xs text-gray-500 text-center">
                        {audioEnabled ? 'Mikrofon aktif - gelombang suara terdeteksi' : 'Mikrofon dimatikan'}
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              <div className="card">
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-lg font-bold flex items-center space-x-2">
                    <Video size={20} />
                    <span>Live Video</span>
                  </h2>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        setVideoEnabled(!videoEnabled)
                        videoEnabledRef.current = !videoEnabled
                      }}
                      className={`p-2 rounded-lg ${videoEnabled ? 'bg-gray-100' : 'bg-red-100 text-red-600'}`}
                    >
                      {videoEnabled ? <Video size={20} /> : <VideoOff size={20} />}
                    </button>
                    <button
                      onClick={() => {
                        setAudioEnabled(!audioEnabled)
                        audioEnabledRef.current = !audioEnabled
                      }}
                      className={`p-2 rounded-lg ${audioEnabled ? 'bg-gray-100' : 'bg-red-100 text-red-600'}`}
                    >
                      {audioEnabled ? <Mic size={20} /> : <MicOff size={20} />}
                    </button>
                  </div>
                </div>
                <div className="relative bg-gray-900 rounded-lg overflow-hidden aspect-video">
                  {videoEnabled ? (
                    <Webcam
                      ref={webcamRef}
                      audio={false}
                      screenshotFormat="image/jpeg"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      <VideoOff size={48} className="text-gray-600" />
                    </div>
                  )}
                </div>
              </div>

              {/* Custom Indicators Display */}
              {indicators.length > 0 && (
                <div className="card">
                  <h2 className="text-lg font-bold flex items-center space-x-2 mb-4">
                    <Activity size={20} />
                    <span>Custom Indicators</span>
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {indicators.map((indicator) => (
                      <div key={indicator.id} className="p-3 bg-gray-50 rounded border">
                        <p className="font-medium text-sm">{indicator.name}</p>
                        <p className="text-xs text-gray-500 mt-1">{indicator.description}</p>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-3">
                    <strong>Catatan:</strong> Analisis berdasarkan indicators ini akan dilakukan setelah wawancara selesai.
                  </p>
                </div>
              )}
            </div>

            {/* Right Sidebar */}
            <div className="space-y-6">
              <EmotionIndicator
                emotion={currentEmotion.emotion}
                confidence={currentEmotion.confidence}
                stability={emotionStability}
              />

              <div className="card">
                <h2 className="text-lg font-bold flex items-center space-x-2 mb-4">
                  <Activity size={20} />
                  <span>Real-time Monitoring</span>
                </h2>
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Stabilitas Emosi</span>
                      <span className="font-medium">{(emotionStability * 100).toFixed(0)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-500 h-2 rounded-full transition-all"
                        style={{ width: `${emotionStability * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-3">
                  Data real-time untuk monitoring selama wawancara.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
