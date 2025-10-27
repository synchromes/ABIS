import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { ArrowLeft, CheckCircle2, TrendingUp, FileText, Download } from 'lucide-react'

export default function InterviewAssessment() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [interview, setInterview] = useState(null)
  const [assessment, setAssessment] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    try {
      // Load interview details
      const interviewRes = await api.get(`/interviews/${id}`)
      setInterview(interviewRes.data)

      // Load assessment results
      const assessmentRes = await api.get(`/interviews/${id}/assessment`)
      setAssessment(assessmentRes.data)
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Gagal memuat assessment'
      toast.error(errorMsg)
      if (error.response?.status === 400) {
        // Not yet processed
        setTimeout(() => navigate(`/interviews`), 2000)
      }
    } finally {
      setLoading(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 60) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (score >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Sangat Baik'
    if (score >= 60) return 'Baik'
    if (score >= 40) return 'Cukup'
    return 'Perlu Ditingkatkan'
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!assessment) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">Assessment belum tersedia</p>
          <button onClick={() => navigate('/interviews')} className="btn btn-primary">
            Kembali ke Daftar Interview
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/interviews')}
            className="btn btn-ghost"
          >
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">AI Assessment Results</h1>
            <p className="text-gray-600 mt-1">{interview?.candidate_name} - {interview?.position}</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Link
            to={`/interview/${id}`}
            className="btn btn-outline"
          >
            <FileText size={18} />
            Detail Interview
          </Link>
          <button
            onClick={() => toast.success('Export feature coming soon')}
            className="btn btn-primary"
          >
            <Download size={18} />
            Export PDF
          </button>
        </div>
      </div>

      {/* Overall Score Card */}
      <div className="card bg-gradient-to-r from-primary-50 to-purple-50 border-2 border-primary-200 mb-6">
        <div className="text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <TrendingUp className="text-primary-600" size={24} />
            <h2 className="text-lg font-semibold text-gray-700">Overall Score</h2>
          </div>
          <div className="text-6xl font-bold text-primary-600 mb-2">
            {parseFloat(assessment.overall_score || 0).toFixed(1)}
          </div>
          <div className="text-lg text-gray-600">
            {getScoreLabel(assessment.overall_score)}
          </div>
          <div className="mt-4 flex items-center justify-center gap-6 text-sm">
            <div>
              <span className="text-gray-600">Total Indikator:</span>
              <span className="font-semibold ml-1">{assessment.total_indicators}</span>
            </div>
            <div className="w-px h-6 bg-gray-300"></div>
            <div>
              <span className="text-gray-600">Teranalisis:</span>
              <span className="font-semibold ml-1">{assessment.assessed_indicators}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Indicators Assessment */}
      <div className="space-y-4">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <CheckCircle2 className="text-primary-600" />
          Detailed Assessment
        </h2>

        {assessment.indicators.map((indicator, index) => (
          <div key={indicator.id} className="card hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700 font-bold text-sm">
                    {index + 1}
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900">{indicator.name}</h3>
                  {indicator.weight !== 1.0 && (
                    <span className="badge badge-outline text-xs">
                      Bobot: {indicator.weight}x
                    </span>
                  )}
                </div>
                {indicator.description && (
                  <p className="text-sm text-gray-600 ml-11">{indicator.description}</p>
                )}
              </div>

              {indicator.assessment && (
                <div className={`px-4 py-2 rounded-lg border-2 ${getScoreColor(parseFloat(indicator.assessment.score || 0))}`}>
                  <div className="text-2xl font-bold text-center">
                    {parseFloat(indicator.assessment.score || 0).toFixed(0)}
                  </div>
                  <div className="text-xs text-center opacity-75">
                    {getScoreLabel(parseFloat(indicator.assessment.score || 0))}
                  </div>
                </div>
              )}
            </div>

            {indicator.assessment ? (
              <div className="space-y-3 ml-11">
                {/* Reasoning */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Reasoning:
                  </label>
                  <p className="text-sm text-gray-900 bg-gray-50 p-3 rounded-lg border">
                    {indicator.assessment.reasoning}
                  </p>
                </div>

                {/* Evidence */}
                {indicator.assessment.evidence && indicator.assessment.evidence !== 'Tidak ditemukan bukti spesifik dalam transkrip.' && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Evidence from Transcript:
                    </label>
                    <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                      {indicator.assessment.evidence.split('|').map((evidence, i) => (
                        <div key={i} className="flex items-start gap-2 mb-2 last:mb-0">
                          <div className="w-1.5 h-1.5 rounded-full bg-blue-600 mt-1.5 flex-shrink-0"></div>
                          <p className="text-sm text-gray-900 italic">"{evidence.trim()}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {indicator.assessment.evidence === 'Tidak ditemukan bukti spesifik dalam transkrip.' && (
                  <div className="bg-yellow-50 p-3 rounded-lg border border-yellow-200">
                    <p className="text-sm text-yellow-800">
                      ⚠️ Tidak ditemukan bukti spesifik dalam transkrip untuk indikator ini.
                    </p>
                  </div>
                )}
              </div>
            ) : (
              <div className="ml-11 bg-gray-50 p-3 rounded-lg border">
                <p className="text-sm text-gray-500">Belum ada assessment untuk indikator ini</p>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Transcript Section (Optional) */}
      {interview?.transcript && (
        <div className="card mt-8">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Full Transcript</h2>
          <div className="bg-gray-50 p-4 rounded-lg border max-h-96 overflow-y-auto">
            <p className="text-sm text-gray-900 whitespace-pre-wrap leading-relaxed">
              {interview.transcript}
            </p>
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Transcript length: {interview.transcript.length} characters
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex justify-between items-center mt-8 pt-6 border-t">
        <button
          onClick={() => navigate('/interviews')}
          className="btn btn-outline"
        >
          Kembali ke Daftar
        </button>
        <div className="flex gap-3">
          <Link
            to={`/interview/${id}/report`}
            className="btn btn-secondary"
          >
            Lihat Laporan Lengkap
          </Link>
          <button
            onClick={() => {
              toast.promise(
                api.post(`/interviews/${id}/process`),
                {
                  loading: 'Re-processing...',
                  success: 'Interview berhasil diproses ulang!',
                  error: 'Gagal memproses ulang'
                }
              ).then(() => loadData())
            }}
            className="btn btn-primary"
          >
            Re-process Assessment
          </button>
        </div>
      </div>
    </div>
  )
}
