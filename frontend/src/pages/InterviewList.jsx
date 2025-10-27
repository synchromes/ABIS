import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { Plus, Search, Filter, Play } from 'lucide-react'
import { format } from 'date-fns'
import { id as idLocale } from 'date-fns/locale'
import IndicatorsForm from '../components/IndicatorsForm'

export default function InterviewList() {
  const [interviews, setInterviews] = useState([])
  const [filteredInterviews, setFilteredInterviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  // Pagination states
  const [currentPage, setCurrentPage] = useState(1)
  const [itemsPerPage, setItemsPerPage] = useState(10)

  useEffect(() => {
    loadInterviews()
  }, [])

  useEffect(() => {
    filterInterviews()
    setCurrentPage(1) // Reset to first page when filters change
  }, [searchQuery, statusFilter, interviews])

  const loadInterviews = async () => {
    try {
      const response = await api.get('/interviews/')
      setInterviews(response.data)
      setFilteredInterviews(response.data)
    } catch (error) {
      toast.error('Gagal memuat data wawancara')
    } finally {
      setLoading(false)
    }
  }

  const filterInterviews = () => {
    let filtered = interviews

    if (searchQuery) {
      filtered = filtered.filter(
        (i) =>
          i.candidate_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          i.position.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter((i) => i.status === statusFilter)
    }

    setFilteredInterviews(filtered)
  }

  const getStatusBadge = (status) => {
    const badges = {
      scheduled: 'badge badge-info',
      in_progress: 'badge badge-warning',
      completed: 'badge badge-success',
      cancelled: 'badge badge-danger',
    }
    return badges[status] || 'badge'
  }

  const getStatusLabel = (status) => {
    const labels = {
      scheduled: 'Terjadwal',
      in_progress: 'Berlangsung',
      completed: 'Selesai',
      cancelled: 'Dibatalkan',
    }
    return labels[status] || status
  }

  const getProcessingStatusBadge = (status) => {
    const badges = {
      recording: 'badge badge-info',
      processing: 'badge badge-warning',
      completed: 'badge badge-success',
      failed: 'badge badge-danger',
    }
    return badges[status] || 'badge badge-secondary'
  }

  const getProcessingStatusLabel = (status) => {
    const labels = {
      recording: 'Belum Diproses',
      processing: 'Sedang Diproses',
      completed: 'Sudah Diproses',
      failed: 'Gagal',
    }
    return labels[status] || status
  }

  const handleProcessInterview = async (interviewId) => {
    if (!confirm('Apakah Anda yakin ingin memproses wawancara ini? Proses ini akan memakan waktu beberapa menit.')) {
      return
    }

    try {
      toast.loading('Memproses wawancara...', { id: `process-${interviewId}` })
      await api.post(`/interviews/${interviewId}/process`)
      toast.success('Wawancara berhasil diproses!', { id: `process-${interviewId}` })
      loadInterviews()
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Gagal memproses wawancara'
      toast.error(errorMsg, { id: `process-${interviewId}` })
    }
  }

  // Pagination calculations
  const totalItems = filteredInterviews.length
  const totalPages = Math.ceil(totalItems / itemsPerPage)
  const startIndex = (currentPage - 1) * itemsPerPage
  const endIndex = startIndex + itemsPerPage
  const currentItems = filteredInterviews.slice(startIndex, endIndex)
  
  const handlePageChange = (page) => {
    setCurrentPage(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
  
  const handleItemsPerPageChange = (newSize) => {
    setItemsPerPage(newSize)
    setCurrentPage(1) // Reset to first page
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Daftar Wawancara</h1>
          <p className="text-gray-600 mt-1">Kelola sesi wawancara kandidat ASN</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Plus size={20} />
          <span>Buat Wawancara</span>
        </button>
      </div>

      {/* Search & Filters */}
      <div className="card mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Cari kandidat atau posisi..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="input pl-10"
            />
          </div>
          <div className="flex items-center space-x-2">
            <Filter size={20} className="text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input"
            >
              <option value="all">Semua Status</option>
              <option value="scheduled">Terjadwal</option>
              <option value="in_progress">Berlangsung</option>
              <option value="completed">Selesai</option>
              <option value="cancelled">Dibatalkan</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* Items Per Page & Info */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 px-6 py-4 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-3">
            <span className="text-sm font-semibold text-gray-700">Tampilkan</span>
            <select
              value={itemsPerPage}
              onChange={(e) => handleItemsPerPageChange(Number(e.target.value))}
              className="px-4 py-2 border-2 border-blue-300 rounded-lg text-sm font-semibold text-gray-900 bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-colors"
            >
              <option value={10}>10</option>
              <option value={20}>20</option>
              <option value={50}>50</option>
              <option value={100}>100</option>
            </select>
            <span className="text-sm font-semibold text-gray-700">data per halaman</span>
          </div>
          <div className="text-sm text-gray-600">
            Menampilkan <span className="font-bold text-blue-700">{startIndex + 1}</span> - <span className="font-bold text-blue-700">{Math.min(endIndex, totalItems)}</span> dari <span className="font-bold text-blue-700">{totalItems}</span> data
          </div>
        </div>
      </div>

      <div className="card">
        {filteredInterviews.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Tidak ada wawancara ditemukan</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Kandidat</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Posisi</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Jadwal</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Status</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">AI Processing</th>
                  <th className="text-left py-3 px-4 font-medium text-gray-700">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {currentItems.map((interview) => (
                  <tr key={interview.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <p className="font-medium text-gray-900">{interview.candidate_name}</p>
                      {interview.candidate_email && (
                        <p className="text-sm text-gray-500">{interview.candidate_email}</p>
                      )}
                    </td>
                    <td className="py-3 px-4 text-gray-600">{interview.position}</td>
                    <td className="py-3 px-4 text-gray-600 text-sm">
                      {interview.scheduled_at
                        ? format(new Date(interview.scheduled_at), 'dd MMM yyyy, HH:mm', { locale: idLocale })
                        : '-'}
                    </td>
                    <td className="py-3 px-4">
                      <span className={getStatusBadge(interview.status)}>
                        {getStatusLabel(interview.status)}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={getProcessingStatusBadge(interview.processing_status || 'recording')}>
                        {getProcessingStatusLabel(interview.processing_status || 'recording')}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex flex-wrap gap-2">
                        <Link
                          to={`/interview/${interview.id}`}
                          className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                        >
                          Detail
                        </Link>
                        {interview.status === 'completed' && interview.processing_status === 'recording' && (
                          <button
                            onClick={() => handleProcessInterview(interview.id)}
                            className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
                          >
                            <Play size={14} />
                            Process
                          </button>
                        )}
                        {interview.status === 'completed' && interview.processing_status === 'completed' && (
                          <Link
                            to={`/interview/${interview.id}/assessment`}
                            className="text-purple-600 hover:text-purple-700 text-sm font-medium"
                          >
                            Assessment
                          </Link>
                        )}
                        {interview.status === 'completed' && (
                          <Link
                            to={`/interview/${interview.id}/report`}
                            className="text-green-600 hover:text-green-700 text-sm font-medium"
                          >
                            Laporan
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        
        {/* Pagination Controls */}
        {filteredInterviews.length > 0 && totalPages > 1 && (
          <div className="flex items-center justify-between border-t px-6 py-4">
            <div className="text-sm text-gray-600">
              Halaman <span className="font-medium">{currentPage}</span> dari <span className="font-medium">{totalPages}</span>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Previous Button */}
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={`px-3 py-1 border rounded-lg text-sm font-medium transition-colors ${
                  currentPage === 1
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Sebelumnya
              </button>
              
              {/* Page Numbers */}
              <div className="flex items-center space-x-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                  // Show first page, last page, current page, and pages around current
                  const showPage = 
                    page === 1 || 
                    page === totalPages || 
                    (page >= currentPage - 1 && page <= currentPage + 1)
                  
                  const showEllipsis = 
                    (page === currentPage - 2 && currentPage > 3) || 
                    (page === currentPage + 2 && currentPage < totalPages - 2)
                  
                  if (showEllipsis) {
                    return <span key={page} className="px-2 text-gray-400">...</span>
                  }
                  
                  if (!showPage) return null
                  
                  return (
                    <button
                      key={page}
                      onClick={() => handlePageChange(page)}
                      className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                        currentPage === page
                          ? 'bg-primary-600 text-white'
                          : 'bg-white text-gray-700 hover:bg-gray-50 border'
                      }`}
                    >
                      {page}
                    </button>
                  )
                })}
              </div>
              
              {/* Next Button */}
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`px-3 py-1 border rounded-lg text-sm font-medium transition-colors ${
                  currentPage === totalPages
                    ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                Selanjutnya
              </button>
            </div>
          </div>
        )}
      </div>

      {showCreateModal && (
        <CreateInterviewModal
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false)
            loadInterviews()
          }}
        />
      )}
    </div>
  )
}

function CreateInterviewModal({ onClose, onSuccess }) {
  const [formData, setFormData] = useState({
    candidate_name: '',
    candidate_email: '',
    candidate_id_number: '',
    position: '',
    scheduled_at: '',
  })
  const [indicators, setIndicators] = useState([])
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState(1) // 1: Basic Info, 2: Indicators

  const handleNext = (e) => {
    e.preventDefault()
    if (!formData.candidate_name || !formData.position) {
      toast.error('Nama kandidat dan posisi harus diisi')
      return
    }
    setStep(2)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (indicators.length === 0) {
      toast.error('Tambahkan minimal 1 indikator')
      return
    }

    setLoading(true)

    try {
      // Create interview
      const response = await api.post('/interviews/', formData)
      const interviewId = response.data.id
      
      // Add indicators
      const indicatorPromises = indicators.map(ind =>
        api.post(`/interviews/${interviewId}/indicators`, {
          name: ind.name,
          description: ind.description || '',
          weight: ind.weight
        })
      )
      
      await Promise.all(indicatorPromises)
      
      toast.success('Wawancara dan indikator berhasil dibuat')
      onSuccess()
    } catch (error) {
      toast.error('Gagal membuat wawancara')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold">Buat Wawancara Baru</h2>
          <div className="flex items-center gap-2 text-sm">
            <span className={`px-3 py-1 rounded ${step === 1 ? 'bg-primary-100 text-primary-700' : 'bg-gray-100'}`}>
              1. Info Dasar
            </span>
            <span className={`px-3 py-1 rounded ${step === 2 ? 'bg-primary-100 text-primary-700' : 'bg-gray-100'}`}>
              2. Indikator
            </span>
          </div>
        </div>
        
        <form onSubmit={step === 1 ? handleNext : handleSubmit} className="space-y-4">{step === 1 ? (
          // Step 1: Basic Info
          <>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nama Kandidat *
            </label>
            <input
              type="text"
              value={formData.candidate_name}
              onChange={(e) => setFormData({ ...formData, candidate_name: e.target.value })}
              className="input"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={formData.candidate_email}
              onChange={(e) => setFormData({ ...formData, candidate_email: e.target.value })}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Nomor Identitas
            </label>
            <input
              type="text"
              value={formData.candidate_id_number}
              onChange={(e) => setFormData({ ...formData, candidate_id_number: e.target.value })}
              className="input"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Posisi *
            </label>
            <input
              type="text"
              value={formData.position}
              onChange={(e) => setFormData({ ...formData, position: e.target.value })}
              className="input"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Jadwal
            </label>
            <input
              type="datetime-local"
              value={formData.scheduled_at}
              onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
              className="input"
            />
          </div>
          </>
          ) : (
            // Step 2: Indicators
            <>
              <IndicatorsForm 
                indicators={indicators}
                onChange={setIndicators}
              />
            </>
          )}
          
          <div className="flex space-x-3 pt-4 border-t">
            {step === 2 && (
              <button
                type="button"
                onClick={() => setStep(1)}
                className="btn btn-outline"
                disabled={loading}
              >
                Kembali
              </button>
            )}
            <button
              type="button"
              onClick={onClose}
              className="btn btn-secondary flex-1"
              disabled={loading}
            >
              Batal
            </button>
            <button
              type="submit"
              className="btn btn-primary flex-1"
              disabled={loading}
            >
              {loading ? 'Menyimpan...' : step === 1 ? 'Lanjut' : 'Simpan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
