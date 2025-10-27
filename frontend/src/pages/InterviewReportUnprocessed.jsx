// Component for unprocessed interview report
import { AlertCircle, Play, ArrowLeft, Clock, FileText } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function UnprocessedInterviewReport({ interview, indicators = [] }) {
  const navigate = useNavigate()

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
        {/* Status Alert */}
        <div className="card bg-yellow-50 border-yellow-200 mb-6">
          <div className="flex items-start gap-3">
            <AlertCircle size={24} className="text-yellow-600 flex-shrink-0 mt-1" />
            <div className="flex-1">
              <h3 className="font-semibold text-yellow-900 mb-2">
                Wawancara Belum Diproses
              </h3>
              <p className="text-sm text-yellow-800 mb-4">
                Interview ini sudah selesai dilakukan, tetapi belum diproses dengan AI untuk menghasilkan assessment. 
                Silakan proses terlebih dahulu untuk mendapatkan analisis lengkap.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => navigate('/interviews')}
                  className="btn btn-primary flex items-center gap-2"
                >
                  <Play size={18} />
                  Kembali ke List & Proses
                </button>
                <button
                  onClick={() => navigate(`/interview/${interview.id}`)}
                  className="btn btn-outline"
                >
                  Lihat Detail Interview
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Interview Info */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">Informasi Wawancara</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-start space-x-3">
              <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <FileText size={20} className="text-primary-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Kandidat</p>
                <p className="font-medium text-gray-900">{interview?.candidate_name}</p>
                <p className="text-sm text-gray-500">{interview?.candidate_email}</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                <Clock size={20} className="text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-gray-600">Durasi</p>
                <p className="font-medium text-gray-900">
                  {interview?.duration_seconds 
                    ? `${Math.floor(interview.duration_seconds / 60)} menit ${interview.duration_seconds % 60} detik`
                    : 'Belum tersedia'}
                </p>
                <p className="text-sm text-gray-500">
                  {interview?.ended_at ? new Date(interview.ended_at).toLocaleString('id-ID') : '-'}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Custom Indicators Preview */}
        {indicators.length > 0 && (
          <div className="card mb-6">
            <h2 className="text-xl font-bold text-gray-900 mb-4">
              Custom Indicators yang Dikonfigurasi
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Indikator-indikator berikut akan digunakan untuk menilai kandidat setelah interview diproses dengan AI.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {indicators.map((indicator, index) => (
                <div key={indicator.id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                      <span className="text-primary-700 font-bold text-sm">{index + 1}</span>
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900 mb-1">{indicator.name}</h3>
                      <p className="text-sm text-gray-600 mb-2">{indicator.description}</p>
                      <span className="inline-block text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded">
                        Weight: {parseFloat(indicator.weight).toFixed(1)}x
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {indicators.length === 0 && (
          <div className="card bg-orange-50 border-orange-200 mb-6">
            <div className="flex items-start gap-3">
              <AlertCircle size={20} className="text-orange-600 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-orange-900 mb-1">
                  Belum Ada Custom Indicators
                </h3>
                <p className="text-sm text-orange-800">
                  Interview ini belum memiliki custom indicators. Silakan tambahkan indicators terlebih dahulu 
                  sebelum memproses interview untuk mendapatkan assessment yang relevan.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="card bg-blue-50 border-blue-200">
          <h3 className="font-semibold text-blue-900 mb-3">Langkah Selanjutnya:</h3>
          <ol className="space-y-2 text-sm text-blue-800">
            <li className="flex items-start gap-2">
              <span className="font-bold">1.</span>
              <span>Pastikan interview sudah selesai dilakukan (status: Completed)</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">2.</span>
              <span>
                Pastikan sudah ada custom indicators (minimal 1 indicator).
                {indicators.length === 0 && <strong> Tambahkan indicators di halaman interview list.</strong>}
              </span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">3.</span>
              <span>Klik tombol "Process" di halaman Interview List untuk memulai AI processing</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">4.</span>
              <span>Tunggu beberapa menit hingga processing selesai (status berubah menjadi "Sudah Diproses")</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="font-bold">5.</span>
              <span>Kembali ke halaman ini untuk melihat hasil assessment lengkap dengan grafik dan nilai</span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  )
}
