import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { Download, ArrowLeft, CheckCircle, AlertCircle, XCircle, Save, Info, Edit, BarChart3, TrendingUp, Activity } from 'lucide-react'
import { format } from 'date-fns'
import { id as idLocale } from 'date-fns/locale'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart as RechartsRadar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, Cell } from 'recharts'

export default function InterviewReport() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [interview, setInterview] = useState(null)
  const [scores, setScores] = useState(null)
  const [assessment, setAssessment] = useState(null)
  const [indicators, setIndicators] = useState([])
  const [transcript, setTranscript] = useState([])
  const [emotions, setEmotions] = useState(null)
  const [loading, setLoading] = useState(true)
  const [manualScores, setManualScores] = useState({})
  const [interviewerNotes, setInterviewerNotes] = useState('')
  const [weights, setWeights] = useState({ ai_weight: 60, manual_weight: 40 })
  const [saving, setSaving] = useState(false)
  const [useNewAssessment, setUseNewAssessment] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)

  useEffect(() => {
    loadReportData()
    loadWeights()
    loadIndicators()
    loadEmotions()
    
    // Poll for processing status if interview is being processed
    const interval = setInterval(() => {
      if (isProcessing) {
        loadReportData()
      }
    }, 5000) // Check every 5 seconds
    
    return () => clearInterval(interval)
  }, [id, isProcessing])
  
  const loadWeights = async () => {
    try {
      const response = await api.get('/settings/scoring-weights')
      setWeights(response.data)
    } catch (error) {
      console.error('Failed to load weights:', error)
      // Use defaults if failed
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
  
  const loadEmotions = async () => {
    try {
      console.log(`[Report] Loading emotions for interview ${id}...`)
      const response = await api.get(`/interviews/${id}/emotions`)
      console.log(`[Report] Emotions response:`, response.data)
      setEmotions(response.data)
      
      if (response.data.total_detections === 0) {
        console.warn('[Report] No emotion data found for this interview')
      }
    } catch (error) {
      console.error('[Report] Failed to load emotions:', error)
      console.error('[Report] Error details:', error.response?.data)
    }
  }

  const loadReportData = async () => {
    try {
      const response = await api.get(`/interviews/${id}`)
      setInterview(response.data)
      
      // Check if processing
      if (response.data.processing_status === 'processing') {
        setIsProcessing(true)
      } else {
        setIsProcessing(false)
      }
      
      // Try to load new assessment (custom indicators)
      if (response.data.processing_status === 'completed') {
        try {
          const assessmentRes = await api.get(`/interviews/${id}/assessment`)
          setAssessment(assessmentRes.data)
          setUseNewAssessment(true)
          
          // Pre-fill manual scores if already entered
          const existingManualScores = {}
          assessmentRes.data.indicators.forEach(indicator => {
            if (indicator.assessment?.manual_score) {
              existingManualScores[indicator.id] = parseFloat(indicator.assessment.manual_score)
            }
          })
          setManualScores(existingManualScores)
          
          // Pre-fill notes if exists
          const firstIndicator = assessmentRes.data.indicators.find(i => i.assessment?.interviewer_notes)
          if (firstIndicator?.assessment?.interviewer_notes) {
            setInterviewerNotes(firstIndicator.assessment.interviewer_notes)
          }
        } catch (assessmentError) {
          console.log('No custom assessment, falling back to old scores')
          // Fall back to old BerAKHLAK scores
          if (response.data.scores) {
            setScores(response.data.scores)
          }
        }
      } else {
        // Use old scores if not processed
        if (response.data.scores) {
          setScores(response.data.scores)
        }
      }
      
      if (response.data.transcript_entries) {
        setTranscript(response.data.transcript_entries)
      }
    } catch (error) {
      toast.error('Gagal memuat laporan')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleManualScoreChange = (indicatorId, value) => {
    const numValue = parseFloat(value)
    if (value === '' || (numValue >= 0 && numValue <= 100)) {
      setManualScores(prev => ({
        ...prev,
        [indicatorId]: numValue || 0
      }))
    }
  }

  const calculateCombined = (indicator) => {
    const aiScore = parseFloat(indicator.assessment?.score || 0)
    const manualScore = parseFloat(manualScores[indicator.id] || 0)
    
    if (manualScore > 0) {
      const combined = (aiScore * weights.ai_weight / 100) + (manualScore * weights.manual_weight / 100)
      return combined.toFixed(1)
    }
    return aiScore.toFixed(1)
  }

  const handleSaveManualScores = async () => {
    setSaving(true)
    try {
      await api.put(`/interviews/${id}/manual-scores`, {
        manual_scores: manualScores,
        interviewer_notes: interviewerNotes
      })
      toast.success('Skor manual berhasil disimpan!')
      loadReportData() // Reload to show updated combined scores
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Gagal menyimpan skor manual')
      console.error(error)
    } finally {
      setSaving(false)
    }
  }

  const downloadReport = async (format) => {
    try {
      toast.loading('Generating report...')
      // In real implementation, call API to generate PDF/JSON
      toast.success(`Laporan ${format.toUpperCase()} berhasil di-download`)
    } catch (error) {
      toast.error('Gagal men-download laporan')
    }
  }

  const getRecommendationIcon = (recommendation) => {
    const icons = {
      layak: { Icon: CheckCircle, color: 'text-green-500' },
      dipertimbangkan: { Icon: AlertCircle, color: 'text-yellow-500' },
      tidak_layak: { Icon: XCircle, color: 'text-red-500' },
    }
    return icons[recommendation] || icons.dipertimbangkan
  }

  const dimensions = [
    { key: 'berorientasi_pelayanan', label: 'Berorientasi Pelayanan' },
    { key: 'akuntabel', label: 'Akuntabel' },
    { key: 'kompeten', label: 'Kompeten' },
    { key: 'harmonis', label: 'Harmonis' },
    { key: 'loyal', label: 'Loyal' },
    { key: 'adaptif', label: 'Adaptif' },
    { key: 'kolaboratif', label: 'Kolaboratif' },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  const berakhlakScores = {}
  dimensions.forEach(dim => {
    berakhlakScores[dim.key] = scores?.[`${dim.key}_ai`] || 0
  })

  // Prepare chart data for visualizations
  const prepareChartData = () => {
    if (!assessment || !assessment.indicators) return []
    
    return assessment.indicators.map(indicator => {
      const aiScore = parseFloat(indicator.assessment?.score || 0)
      const manualScore = parseFloat(indicator.assessment?.manual_score || manualScores[indicator.id] || 0)
      const combined = manualScore > 0 
        ? (aiScore * weights.ai_weight / 100) + (manualScore * weights.manual_weight / 100)
        : aiScore
      
      return {
        name: indicator.name.length > 15 ? indicator.name.substring(0, 15) + '...' : indicator.name,
        fullName: indicator.name,
        'AI Score': aiScore,
        'Manual Score': manualScore,
        'Combined': parseFloat(combined.toFixed(1))
      }
    })
  }
  
  const prepareRadarData = () => {
    if (!assessment || !assessment.indicators) return []
    
    return assessment.indicators.map(indicator => {
      const aiScore = parseFloat(indicator.assessment?.score || 0)
      const manualScore = parseFloat(indicator.assessment?.manual_score || manualScores[indicator.id] || 0)
      const combined = manualScore > 0 
        ? (aiScore * weights.ai_weight / 100) + (manualScore * weights.manual_weight / 100)
        : aiScore
      
      return {
        indicator: indicator.name.length > 12 ? indicator.name.substring(0, 12) + '...' : indicator.name,
        score: parseFloat(combined.toFixed(1)),
        fullMark: 100
      }
    })
  }

  // Always show main report page (even if processing or no assessment yet)
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/interviews')}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Laporan Wawancara</h1>
              <p className="text-gray-600">{interview?.candidate_name} - {interview?.position}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Processing Status Notice */}
        {(isProcessing || !assessment) && (
          <div className="card bg-yellow-50 border-yellow-200 mb-6">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-yellow-600"></div>
                <div className="flex-1">
                  <h3 className="font-semibold text-yellow-900">AI Sedang Memproses Penilaian</h3>
                  <p className="text-sm text-yellow-800">
                    Sistem AI sedang menganalisis transkrip dan memberikan penilaian untuk setiap indikator.
                    Proses ini memakan waktu 30-90 detik. Anda sudah bisa memasukkan nilai manual terlebih dahulu.
                    Halaman akan otomatis ter-update saat AI selesai.
                  </p>
                </div>
              </div>
            </div>
          )}
          
          {/* Completed Assessment Notice */}
          {!isProcessing && assessment && (
            <div className="card bg-green-50 border-green-200 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <CheckCircle className="text-green-600" size={24} />
                  <div>
                    <h3 className="font-semibold text-green-900">AI Assessment Selesai!</h3>
                    <p className="text-sm text-green-700">
                      Wawancara ini sudah diproses dengan sistem penilaian custom indicators.
                      Anda dapat menambahkan nilai manual untuk hasil yang lebih akurat.
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => navigate(`/interview/${id}/assessment`)}
                  className="btn btn-primary"
                >
                  Lihat Assessment Lengkap
                </button>
              </div>
            </div>
          )}

          {/* Quick Summary */}
          {assessment && (
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
            <div className="card">
              <p className="text-sm text-gray-600 mb-1">Overall Score</p>
              <p className="text-3xl font-bold text-primary-600">
                {parseFloat(assessment?.overall_score || 0).toFixed(1)}
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {assessment?.assessed_indicators}/{assessment?.total_indicators} indicators
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-600 mb-1">Durasi Wawancara</p>
              <p className="text-3xl font-bold text-gray-900">
                {interview?.duration_seconds 
                  ? `${Math.floor(interview.duration_seconds / 60)} menit`
                  : '-'}
              </p>
            </div>
            <div className="card">
              <p className="text-sm text-gray-600 mb-1">Status</p>
              <p className="text-lg font-semibold text-green-600">
                Sudah Diproses
              </p>
              <p className="text-sm text-gray-500 mt-1">
                {interview?.processed_at ? format(new Date(interview.processed_at), 'dd MMM yyyy, HH:mm', { locale: idLocale }) : '-'}
              </p>
            </div>
          </div>
          )}

          {/* Emotion Distribution Charts - Separated */}
          {emotions && emotions.total_detections > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              
              {/* Facial Emotion Chart */}
              {emotions.facial_emotion_distribution && Object.keys(emotions.facial_emotion_distribution).length > 0 && (
                <div className="card">
                  <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <Activity size={24} className="text-blue-600" />
                    Emosi Wajah (Facial)
                  </h2>
                  
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart 
                      data={Object.entries(emotions.facial_emotion_distribution).map(([emotion, percentage]) => ({
                        emotion: emotion.charAt(0).toUpperCase() + emotion.slice(1),
                        percentage: parseFloat(percentage)
                      }))}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} label={{ value: 'Percentage (%)', position: 'bottom' }} />
                      <YAxis type="category" dataKey="emotion" width={70} />
                      <Tooltip 
                        formatter={(value) => `${value}%`}
                        contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
                      />
                      <Bar dataKey="percentage" radius={[0, 8, 8, 0]}>
                        {Object.entries(emotions.facial_emotion_distribution).map(([emotion, percentage], index) => (
                          <Cell 
                            key={`facial-${index}`} 
                            fill={{
                              'happy': '#10b981',
                              'neutral': '#6b7280',
                              'sad': '#3b82f6',
                              'angry': '#ef4444',
                              'surprise': '#f59e0b',
                              'fear': '#8b5cf6',
                              'disgust': '#ec4899'
                            }[emotion] || '#8b5cf6'} 
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                  
                  {/* Facial Stats */}
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                      <p className="text-xs text-blue-700 font-medium">Emosi Dominan</p>
                      <p className="text-lg font-bold text-blue-900 capitalize">{emotions.dominant_facial_emotion}</p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <p className="text-xs text-green-700 font-medium">Avg Confidence</p>
                      <p className="text-lg font-bold text-green-900">{(emotions.average_facial_confidence * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Speech Emotion Chart */}
              {emotions.speech_emotion_distribution && Object.keys(emotions.speech_emotion_distribution).length > 0 && (
                <div className="card">
                  <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <Activity size={24} className="text-purple-600" />
                    Emosi Suara (Speech)
                  </h2>
                  
                  <ResponsiveContainer width="100%" height={280}>
                    <BarChart 
                      data={Object.entries(emotions.speech_emotion_distribution).map(([emotion, percentage]) => ({
                        emotion: emotion.charAt(0).toUpperCase() + emotion.slice(1),
                        percentage: parseFloat(percentage)
                      }))}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" domain={[0, 100]} label={{ value: 'Percentage (%)', position: 'bottom' }} />
                      <YAxis type="category" dataKey="emotion" width={70} />
                      <Tooltip 
                        formatter={(value) => `${value}%`}
                        contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc', borderRadius: '8px' }}
                      />
                      <Bar dataKey="percentage" radius={[0, 8, 8, 0]}>
                        {Object.entries(emotions.speech_emotion_distribution).map(([emotion, percentage], index) => (
                          <Cell 
                            key={`speech-${index}`} 
                            fill={{
                              'calm': '#10b981',
                              'confident': '#3b82f6',
                              'nervous': '#ef4444',
                              'excited': '#f59e0b',
                              'tired': '#6b7280',
                              'neutral': '#8b5cf6'
                            }[emotion] || '#9ca3af'} 
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                  
                  {/* Speech Stats */}
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <div className="p-3 bg-purple-50 rounded-lg border border-purple-200">
                      <p className="text-xs text-purple-700 font-medium">Intonasi Dominan</p>
                      <p className="text-lg font-bold text-purple-900 capitalize">{emotions.dominant_speech_emotion}</p>
                    </div>
                    <div className="p-3 bg-green-50 rounded-lg border border-green-200">
                      <p className="text-xs text-green-700 font-medium">Avg Confidence</p>
                      <p className="text-lg font-bold text-green-900">{(emotions.average_speech_confidence * 100).toFixed(1)}%</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Overall Emotion Summary */}
          {emotions && emotions.total_detections > 0 && (
            <div className="card mb-8">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Ringkasan Emosi</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-blue-800 font-semibold mb-1">Stabilitas Emosi</p>
                  <p className="text-3xl font-bold text-blue-600">{(emotions.emotion_stability * 100).toFixed(1)}%</p>
                  <p className="text-xs text-blue-600 mt-1">
                    {emotions.emotion_stability >= 0.7 ? 'Sangat Stabil' : 
                     emotions.emotion_stability >= 0.5 ? 'Cukup Stabil' : 'Kurang Stabil'}
                  </p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                  <p className="text-green-800 font-semibold mb-1">Confidence Rata-rata</p>
                  <p className="text-3xl font-bold text-green-600">{(emotions.average_confidence * 100).toFixed(1)}%</p>
                  <p className="text-xs text-green-600 mt-1">Gabungan wajah & suara</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg border border-purple-200">
                  <p className="text-purple-800 font-semibold mb-1">Total Deteksi</p>
                  <p className="text-3xl font-bold text-purple-600">{emotions.total_detections}</p>
                  <p className="text-xs text-purple-600 mt-1">Emosi terdeteksi</p>
                </div>
              </div>
            </div>
          )}

          {/* Score Visualizations */}
          {assessment && assessment.indicators && assessment.indicators.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {/* Bar Chart */}
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <BarChart3 size={20} />
                Grafik Perbandingan Skor
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={prepareChartData()}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
                    formatter={(value) => `${value}/100`}
                  />
                  <Legend />
                  <Bar dataKey="AI Score" fill="#3b82f6" />
                  <Bar dataKey="Manual Score" fill="#10b981" />
                  <Bar dataKey="Combined" fill="#8b5cf6" />
                </BarChart>
              </ResponsiveContainer>
              <p className="text-xs text-gray-500 mt-2 text-center">
                Perbandingan skor AI, Manual, dan Gabungan per indikator
              </p>
            </div>

            {/* Radar Chart */}
            <div className="card">
              <h2 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
                <TrendingUp size={20} />
                Radar Chart Combined Scores
              </h2>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsRadar>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="indicator" tick={{ fontSize: 11 }} />
                  <PolarRadiusAxis angle={90} domain={[0, 100]} />
                  <Radar 
                    name="Combined Score" 
                    dataKey="score" 
                    data={prepareRadarData()}
                    stroke="#8b5cf6" 
                    fill="#8b5cf6" 
                    fillOpacity={0.6} 
                  />
                  <Tooltip formatter={(value) => `${value}/100`} />
                  <Legend />
                </RechartsRadar>
              </ResponsiveContainer>
              <p className="text-xs text-gray-500 mt-2 text-center">
                Visualisasi 360° dari semua indikator
              </p>
            </div>
          </div>
          )}

          {/* Manual Scoring Form */}
          <div className="card mb-8">
            <div className="border-b pb-4 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                    <Edit size={20} />
                    Input Nilai Manual
                  </h2>
                  <p className="text-sm text-gray-600 mt-1">
                    {isProcessing 
                      ? 'Anda dapat mulai memasukkan nilai manual sambil menunggu AI selesai memproses. Nilai AI akan muncul setelah processing selesai.'
                      : 'Tambahkan penilaian manual untuk setiap indikator. Skor gabungan akan dihitung otomatis.'}
                  </p>
                </div>
              </div>
              <div className="mt-3 flex items-center gap-2 text-sm text-gray-600">
                <Info size={16} />
                <span>
                  Kombinasi Skor: AI ({weights.ai_weight}%) + Manual ({weights.manual_weight}%)
                  {isProcessing && ' (AI score akan muncul setelah processing selesai)'}
                </span>
              </div>
            </div>

            {/* Indicators Manual Scoring */}
            <div className="space-y-6">
              {!indicators || indicators.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-300 mx-auto mb-4"></div>
                  <p>Memuat indikator...</p>
                  <p className="text-sm mt-2">Mohon tunggu sebentar...</p>
                </div>
              ) : (
                indicators.map((indicator) => {
                  // Get AI assessment if available
                  const aiAssessment = assessment?.indicators?.find(i => i.id === indicator.id)
                  return (
                <div key={indicator.id} className="border-b pb-6 last:border-b-0">
                  <div className="mb-4">
                    <h3 className="font-bold text-lg text-gray-900">{indicator.name}</h3>
                    <p className="text-sm text-gray-600">{indicator.description}</p>
                    <span className="inline-block mt-1 text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                      Bobot: {parseFloat(indicator.weight).toFixed(1)}x
                    </span>
                  </div>

                  {/* Score Inputs Grid */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                    {/* AI Score (Read-only) */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        🤖 AI Score
                      </label>
                      {isProcessing ? (
                        <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-yellow-50 text-yellow-700 font-semibold flex items-center justify-center gap-2">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-600"></div>
                          <span>Processing...</span>
                        </div>
                      ) : (
                        <input
                          type="number"
                          readOnly
                          value={aiAssessment?.assessment?.score || 0}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-700 font-semibold"
                        />
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        {isProcessing ? 'Sedang diproses AI...' : 'From AI analysis'}
                      </p>
                    </div>

                    {/* Manual Score (Input) */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        👤 Manual Score
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="100"
                        value={manualScores[indicator.id] || ''}
                        onChange={(e) => handleManualScoreChange(indicator.id, e.target.value)}
                        className="w-full px-3 py-2 border border-primary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-semibold"
                        placeholder="0-100"
                      />
                      <p className="text-xs text-gray-500 mt-1">Your assessment</p>
                    </div>

                    {/* Combined Score (Calculated) */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        🎯 Combined Score
                      </label>
                      <input
                        type="number"
                        readOnly
                        value={(() => {
                          const aiScore = parseFloat(aiAssessment?.assessment?.score || 0)
                          const manualScore = parseFloat(manualScores[indicator.id] || 0)
                          if (manualScore > 0) {
                            const combined = (aiScore * weights.ai_weight / 100) + (manualScore * weights.manual_weight / 100)
                            return combined.toFixed(1)
                          }
                          return aiScore.toFixed(1)
                        })()}
                        className="w-full px-3 py-2 border border-green-300 rounded-lg bg-green-50 text-green-700 font-bold text-lg"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        {manualScores[indicator.id] > 0
                          ? `AI(${weights.ai_weight}%) + Manual(${weights.manual_weight}%)`
                          : 'AI only (no manual score)'}
                      </p>
                    </div>
                  </div>

                  {/* AI Analysis Details */}
                  {aiAssessment?.assessment && (
                    <details className="mt-3">
                      <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-primary-600">
                        View AI Analysis & Evidence
                      </summary>
                      <div className="mt-3 p-4 bg-gray-50 rounded-lg space-y-3">
                        {aiAssessment?.assessment?.evidence && (
                          <div>
                            <p className="text-xs font-semibold text-gray-700 mb-1">Evidence:</p>
                            <p className="text-sm text-gray-600 italic">"{aiAssessment.assessment.evidence}"</p>
                          </div>
                        )}
                        {aiAssessment?.assessment?.reasoning && (
                          <div>
                            <p className="text-xs font-semibold text-gray-700 mb-1">Reasoning:</p>
                            <p className="text-sm text-gray-600">{aiAssessment.assessment.reasoning}</p>
                          </div>
                        )}
                      </div>
                    </details>
                  )}
                </div>
                  )
                })
              )}
            </div>

            {/* Interviewer Notes */}
            <div className="mt-6 border-t pt-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Catatan Pewawancara (Opsional)
              </label>
              <textarea
                rows="4"
                value={interviewerNotes}
                onChange={(e) => setInterviewerNotes(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Tambahkan catatan umum tentang kandidat, kesan pewawancara, atau hal-hal penting lainnya..."
              />
            </div>

            {/* Save Button */}
            {indicators && indicators.length > 0 && (
            <div className="mt-6 flex items-center justify-between pt-4 border-t">
              <div className="text-sm text-gray-600">
                {Object.keys(manualScores).filter(k => manualScores[k] > 0).length} dari {indicators.length} indikator memiliki nilai manual
              </div>
              <button
                onClick={handleSaveManualScores}
                disabled={saving}
                className={`btn btn-primary flex items-center gap-2 ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <Save size={18} />
                {saving ? 'Menyimpan...' : 'Simpan Nilai Manual'}
              </button>
            </div>
            )}
          </div>

          {/* Transcript */}
          {interview?.transcript && (
            <div className="card mt-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Transkrip</h2>
              <div className="bg-gray-50 p-4 rounded-lg border max-h-96 overflow-y-auto">
                <p className="text-sm text-gray-900 whitespace-pre-wrap leading-relaxed">
                  {interview.transcript}
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    )
}

// Old code below - will be removed in cleanup
const OldFallback = ({ interview, navigate }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/interviews')}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ArrowLeft size={20} />
            </button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Laporan Wawancara (Old - Deprecated)</h1>
              <p className="text-gray-600">{interview?.candidate_name} - {interview?.position}</p>
            </div>
          </div>
          <div className="flex space-x-2">
            {interview?.processing_status === 'recording' && (
              <button
                onClick={() => navigate(`/interviews`)}
                className="btn btn-warning flex items-center space-x-2"
              >
                <AlertCircle size={20} />
                <span>Belum Diproses - Process Dulu</span>
              </button>
            )}
            <button
              onClick={() => downloadReport('pdf')}
              className="btn btn-primary flex items-center space-x-2"
            >
              <Download size={20} />
              <span>Download PDF</span>
            </button>
            <button
              onClick={() => downloadReport('json')}
              className="btn btn-secondary flex items-center space-x-2"
            >
              <Download size={20} />
              <span>Export JSON</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Warning if not processed */}
        {interview?.processing_status !== 'completed' && (
          <div className="card bg-yellow-50 border-yellow-200 mb-6">
            <div className="flex items-center gap-3">
              <AlertCircle className="text-yellow-600" size={24} />
              <div>
                <h3 className="font-semibold text-yellow-900">Interview Belum Diproses</h3>
                <p className="text-sm text-yellow-700">
                  Untuk mendapatkan penilaian AI dengan custom indicators, silakan proses interview terlebih dahulu dari halaman daftar interview.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <p className="text-sm text-gray-600 mb-1">Durasi Wawancara</p>
            <p className="text-3xl font-bold text-gray-900">
              {interview?.duration_seconds 
                ? `${Math.floor(interview.duration_seconds / 60)} menit`
                : '-'}
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 mb-1">Skor AI (BerAKHLAK Lama)</p>
            <p className="text-3xl font-bold text-blue-600">
              {scores?.overall_ai_score?.toFixed(2) || '-'} / 5.0
            </p>
          </div>
          <div className="card">
            <p className="text-sm text-gray-600 mb-1">Skor Akhir</p>
            <p className="text-3xl font-bold text-green-600">
              {scores?.final_score?.toFixed(2) || '-'} / 5.0
            </p>
          </div>
        </div>

        {interview?.recommendation && (
          <div className="card mb-8">
            <div className="flex items-center space-x-4">
              {(() => {
                const { Icon, color } = getRecommendationIcon(interview.recommendation)
                return <Icon size={48} className={color} />
              })()}
              <div>
                <p className="text-sm text-gray-600">Rekomendasi</p>
                <p className="text-2xl font-bold text-gray-900 uppercase">
                  {interview.recommendation}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <div className="card">
            <h2 className="text-xl font-bold mb-6">Grafik Nilai BerAKHLAK</h2>
            <RadarChart scores={berakhlakScores} />
          </div>

          <div className="card">
            <h2 className="text-xl font-bold mb-4">Indikator Perilaku</h2>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-700">Stabilitas Emosi</span>
                  <span className="font-bold">{scores?.emotion_stability?.toFixed(2) || 0} / 5.0</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-blue-500 h-3 rounded-full"
                    style={{ width: `${((scores?.emotion_stability || 0) / 5) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-700">Kejelasan Komunikasi</span>
                  <span className="font-bold">{scores?.speech_clarity?.toFixed(2) || 0} / 5.0</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-green-500 h-3 rounded-full"
                    style={{ width: `${((scores?.speech_clarity || 0) / 5) * 100}%` }}
                  ></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-gray-700">Koherensi Jawaban</span>
                  <span className="font-bold">{scores?.answer_coherence?.toFixed(2) || 0} / 5.0</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-purple-500 h-3 rounded-full"
                    style={{ width: `${((scores?.answer_coherence || 0) / 5) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="card mb-8">
          <h2 className="text-xl font-bold mb-4">Nilai BerAKHLAK Detail</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4">Dimensi</th>
                  <th className="text-center py-3 px-4">Skor AI</th>
                  <th className="text-center py-3 px-4">Skor Manual</th>
                  <th className="text-center py-3 px-4">Rata-rata</th>
                </tr>
              </thead>
              <tbody>
                {dimensions.map(dim => {
                  const aiScore = scores?.[`${dim.key}_ai`] || 0
                  const manualScore = scores?.[`${dim.key}_manual`] || 0
                  const avgScore = manualScore > 0 ? (aiScore + manualScore) / 2 : aiScore
                  
                  return (
                    <tr key={dim.key} className="border-b">
                      <td className="py-3 px-4 font-medium">{dim.label}</td>
                      <td className="py-3 px-4 text-center">{aiScore.toFixed(2)}</td>
                      <td className="py-3 px-4">
                        <input
                          type="number"
                          min="0"
                          max="5"
                          step="0.1"
                          defaultValue={manualScore}
                          onChange={(e) => handleManualScoreChange(dim.key, e.target.value)}
                          className="input text-center w-20 mx-auto"
                        />
                      </td>
                      <td className="py-3 px-4 text-center font-bold">{avgScore.toFixed(2)}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          <button
            onClick={handleSaveManualScores}
            className="btn btn-primary mt-4"
          >
            Simpan Skor Manual
          </button>
        </div>

        {scores?.ai_analysis_summary && (
          <div className="card mb-8">
            <h2 className="text-xl font-bold mb-4">Ringkasan Analisis AI</h2>
            <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono bg-gray-50 p-4 rounded-lg">
              {scores.ai_analysis_summary}
            </pre>
          </div>
        )}

        <div className="card">
          <h2 className="text-xl font-bold mb-4">Transkrip Wawancara</h2>
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {transcript.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Tidak ada transkrip</p>
            ) : (
              transcript.map((entry, index) => (
                <div key={index} className="bg-gray-50 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm text-primary-600">
                      {entry.speaker}
                    </span>
                    <span className="text-xs text-gray-500">
                      {Math.floor(entry.timestamp / 60)}:{Math.floor(entry.timestamp % 60).toString().padStart(2, '0')}
                    </span>
                  </div>
                  <p className="text-gray-800 text-sm">{entry.text}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
