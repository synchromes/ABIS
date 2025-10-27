import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { useAuthStore } from '../stores/authStore'
import { Settings as SettingsIcon, Save, AlertCircle, CheckCircle } from 'lucide-react'

export default function Settings() {
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  
  const [aiWeight, setAiWeight] = useState(60)
  const [manualWeight, setManualWeight] = useState(40)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    // Check if user is admin
    if (user?.role !== 'admin') {
      toast.error('Access denied. Admin only.')
      navigate('/dashboard')
      return
    }
    
    loadSettings()
  }, [user, navigate])

  const loadSettings = async () => {
    try {
      const response = await api.get('/settings/scoring-weights')
      setAiWeight(response.data.ai_weight)
      setManualWeight(response.data.manual_weight)
    } catch (error) {
      toast.error('Failed to load settings')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const handleAiWeightChange = (value) => {
    const numValue = parseInt(value) || 0
    setAiWeight(Math.min(100, Math.max(0, numValue)))
    setManualWeight(100 - Math.min(100, Math.max(0, numValue)))
  }

  const handleManualWeightChange = (value) => {
    const numValue = parseInt(value) || 0
    setManualWeight(Math.min(100, Math.max(0, numValue)))
    setAiWeight(100 - Math.min(100, Math.max(0, numValue)))
  }

  const handleSave = async () => {
    // Validation
    if (aiWeight + manualWeight !== 100) {
      toast.error('Total weights must equal 100%')
      return
    }

    if (aiWeight < 0 || aiWeight > 100 || manualWeight < 0 || manualWeight > 100) {
      toast.error('Weights must be between 0 and 100')
      return
    }

    setSaving(true)
    try {
      await api.put('/settings/scoring-weights', {
        ai_weight: aiWeight,
        manual_weight: manualWeight
      })
      toast.success('Settings saved successfully!')
      loadSettings() // Reload to confirm
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save settings')
      console.error(error)
    } finally {
      setSaving(false)
    }
  }

  const totalWeight = aiWeight + manualWeight
  const isValid = totalWeight === 100

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center gap-3 mb-2">
            <SettingsIcon size={32} className="text-primary-600" />
            <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          </div>
          <p className="text-gray-600">
            Konfigurasi pengaturan aplikasi
          </p>
        </div>

        {/* Scoring Configuration Card */}
        <div className="card">
          <div className="border-b pb-4 mb-6">
            <h2 className="text-xl font-bold text-gray-900">Scoring Configuration</h2>
            <p className="text-sm text-gray-600 mt-1">
              Konfigurasi perhitungan AI dan Manual Skor untuk kombinasi penilaian
            </p>
          </div>

          {/* Weight Inputs */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {/* AI Weight */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🤖 AI Score Weight
              </label>
              <div className="relative">
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={aiWeight}
                  onChange={(e) => handleAiWeightChange(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg font-semibold"
                />
                <span className="absolute right-4 top-3 text-lg font-semibold text-gray-500">%</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Bobot penilaian dari analisis AI (transcription + NLP)
              </p>
            </div>

            {/* Manual Weight */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                👤 Manual Score Weight
              </label>
              <div className="relative">
                <input
                  type="number"
                  min="0"
                  max="100"
                  value={manualWeight}
                  onChange={(e) => handleManualWeightChange(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg font-semibold"
                />
                <span className="absolute right-4 top-3 text-lg font-semibold text-gray-500">%</span>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Bobot penilaian dari pewawancara (subjective assessment)
              </p>
            </div>
          </div>

          {/* Total & Validation */}
          <div className={`p-4 rounded-lg mb-6 ${isValid ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'}`}>
            <div className="flex items-center gap-2">
              {isValid ? (
                <>
                  <CheckCircle size={20} className="text-green-600" />
                  <span className="font-semibold text-green-900">Total: {totalWeight}%</span>
                  <span className="text-green-700">✓ Valid</span>
                </>
              ) : (
                <>
                  <AlertCircle size={20} className="text-red-600" />
                  <span className="font-semibold text-red-900">Total: {totalWeight}%</span>
                  <span className="text-red-700">Must equal 100%</span>
                </>
              )}
            </div>
          </div>

          {/* Example Calculation */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-blue-900 mb-2">Example Calculation:</h3>
            <div className="space-y-1 text-sm">
              <p className="text-blue-800">
                • AI Score: <strong>75/100</strong>
              </p>
              <p className="text-blue-800">
                • Manual Score: <strong>85/100</strong>
              </p>
              <p className="text-blue-800 font-semibold border-t border-blue-300 pt-2 mt-2">
                Combined Score: <strong>{((75 * aiWeight / 100) + (85 * manualWeight / 100)).toFixed(1)}/100</strong>
              </p>
              <p className="text-xs text-blue-600 mt-1">
                Formula: (AI × {aiWeight}%) + (Manual × {manualWeight}%) = {((75 * aiWeight / 100) + (85 * manualWeight / 100)).toFixed(1)}
              </p>
            </div>
          </div>

          {/* Information */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-gray-900 mb-2">Informasi:</h3>
            <ul className="space-y-1 text-sm text-gray-700">
              <li>• Skor yang telah dihitung tidak akan berpengaruh</li>
              <li>• Jika manual skor tidak dimasukan, maka skor sepenuhnya dinilai oleh AI</li>
              <li>• Bobot keduanya harus mencapai 100%</li>
            </ul>
          </div>

          {/* Save Button */}
          <div className="flex items-center justify-between pt-4 border-t">
            <button
              onClick={() => navigate(-1)}
              className="btn btn-outline"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!isValid || saving}
              className={`btn btn-primary flex items-center gap-2 ${!isValid || saving ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <Save size={18} />
              {saving ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>

        {/* Quick Links */}
        {/* <div className="mt-6 card">
          <h3 className="font-semibold text-gray-900 mb-3">Quick Links</h3>
          <div className="space-y-2">
            <button
              onClick={() => navigate('/interviews')}
              className="text-primary-600 hover:text-primary-700 text-sm"
            >
              → Back to Interview List
            </button>
            <br />
            <button
              onClick={() => navigate('/dashboard')}
              className="text-primary-600 hover:text-primary-700 text-sm"
            >
              → Back to Dashboard
            </button>
          </div>
        </div> */}
      </div>
    </div>
  )
}
