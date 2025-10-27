import { Smile, Frown, Meh, AlertCircle } from 'lucide-react'

export default function EmotionIndicator({ emotion, confidence, stability }) {
  const emotionConfig = {
    happy: { icon: Smile, color: 'text-green-500', bg: 'bg-green-50', label: 'Senang' },
    sad: { icon: Frown, color: 'text-blue-500', bg: 'bg-blue-50', label: 'Sedih' },
    angry: { icon: AlertCircle, color: 'text-red-500', bg: 'bg-red-50', label: 'Marah' },
    neutral: { icon: Meh, color: 'text-gray-500', bg: 'bg-gray-50', label: 'Netral' },
    surprise: { icon: AlertCircle, color: 'text-yellow-500', bg: 'bg-yellow-50', label: 'Terkejut' },
    fear: { icon: AlertCircle, color: 'text-purple-500', bg: 'bg-purple-50', label: 'Takut' },
    disgust: { icon: Frown, color: 'text-orange-500', bg: 'bg-orange-50', label: 'Jijik' },
    calm: { icon: Smile, color: 'text-teal-500', bg: 'bg-teal-50', label: 'Tenang' },
  }

  const config = emotionConfig[emotion] || emotionConfig.neutral
  const Icon = config.icon

  return (
    <div className="card">
      <h2 className="text-lg font-bold mb-4">Deteksi Emosi</h2>
      
      <div className={`${config.bg} rounded-xl p-6 mb-4`}>
        <div className="flex items-center justify-center mb-3">
          <Icon size={48} className={config.color} />
        </div>
        <p className="text-center text-2xl font-bold text-gray-900 mb-1">
          {config.label}
        </p>
        <p className="text-center text-sm text-gray-600">
          Confidence: {(confidence * 100).toFixed(0)}%
        </p>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className="text-gray-600">Stabilitas</span>
          <span className={`font-medium ${
            stability > 0.8 ? 'text-green-600' :
            stability > 0.6 ? 'text-yellow-600' :
            'text-red-600'
          }`}>
            {stability > 0.8 ? 'Stabil' : stability > 0.6 ? 'Cukup Stabil' : 'Tidak Stabil'}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all ${
              stability > 0.8 ? 'bg-green-500' :
              stability > 0.6 ? 'bg-yellow-500' :
              'bg-red-500'
            }`}
            style={{ width: `${stability * 100}%` }}
          ></div>
        </div>
      </div>
    </div>
  )
}
