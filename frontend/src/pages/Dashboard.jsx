import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import toast from 'react-hot-toast'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, 
  ResponsiveContainer 
} from 'recharts'
import { 
  Users, Award, CheckCircle2, Brain, TrendingUp, FileText, ArrowRight
} from 'lucide-react'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardStats()
  }, [])

  const loadDashboardStats = async () => {
    try {
      setLoading(true)
      const response = await api.get('/interviews/dashboard/statistics')
      setStats(response.data)
    } catch (error) {
      console.error('Error loading dashboard:', error)
      toast.error('Gagal memuat dashboard')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 font-medium">Loading Dashboard...</p>
        </div>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="text-gray-400 mb-4">📊</div>
          <p className="text-gray-600 mb-4">No data available yet</p>
          <Link to="/interviews" className="btn btn-primary">
            Create First Interview
          </Link>
        </div>
      </div>
    )
  }

  // Prepare score distribution data for simple bar chart
  const scoreDistData = Object.entries(stats.score_distribution).map(([range, count]) => ({
    range,
    count
  }))

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Dashboard Overview
          </h1>
          <p className="text-gray-600">
            Ringkasan sistem wawancara berbasis AI
          </p>
        </div>

        {/* Stats Cards - Simple & Clean */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {/* Total Interviews */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-blue-50 rounded-lg">
                <Users size={24} className="text-blue-600" />
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-1">Total Wawancara</p>
            <p className="text-3xl font-bold text-gray-900">{stats.total_interviews}</p>
          </div>

          {/* Completed */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-green-50 rounded-lg">
                <CheckCircle2 size={24} className="text-green-600" />
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-1">Selesai</p>
            <p className="text-3xl font-bold text-gray-900">{stats.completed_interviews}</p>
            <p className="text-xs text-gray-500 mt-2">
              {Math.round((stats.completed_interviews / stats.total_interviews) * 100) || 0}% completion rate
            </p>
          </div>

          {/* Average Score */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-purple-50 rounded-lg">
                <Award size={24} className="text-purple-600" />
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-1">Rata-rata Skor</p>
            <p className="text-3xl font-bold text-gray-900">{stats.avg_score}</p>
            <p className="text-xs text-gray-500 mt-2">Dari 100</p>
          </div>

          {/* Success Rate */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="p-3 bg-indigo-50 rounded-lg">
                <Brain size={24} className="text-indigo-600" />
              </div>
            </div>
            <p className="text-sm text-gray-600 mb-1">AI Success Rate</p>
            <p className="text-3xl font-bold text-gray-900">{stats.processing_success_rate}%</p>
            <p className="text-xs text-gray-500 mt-2">Processing reliability</p>
          </div>
        </div>

        {/* Score Distribution Chart - Simple */}
        {scoreDistData.some(d => d.count > 0) && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Distribusi Skor Kandidat
            </h3>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={scoreDistData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis 
                  dataKey="range" 
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                />
                <YAxis 
                  tick={{ fill: '#6b7280', fontSize: 12 }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#fff', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px'
                  }}
                />
                <Bar 
                  dataKey="count" 
                  fill="#3b82f6" 
                  radius={[6, 6, 0, 0]}
                  label={{ position: 'top', fill: '#3b82f6', fontSize: 12 }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Top Performers - Simplified */}
        {stats.top_performers.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Award className="mr-2 text-blue-600" size={20} />
              Top 5 Kandidat Terbaik
            </h3>
            <div className="space-y-3">
              {stats.top_performers.map((performer, index) => (
                <div 
                  key={index}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-100"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center font-semibold text-sm">
                      {index + 1}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{performer.name}</p>
                      <p className="text-xs text-gray-500">{performer.position}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-xl font-bold text-blue-600">{performer.score}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Aksi Cepat
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/interviews"
              className="flex items-center justify-between p-4 bg-blue-50 hover:bg-blue-100 rounded-lg border border-blue-200 transition-colors group"
            >
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-blue-600 rounded-lg">
                  <FileText size={20} className="text-white" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Daftar Wawancara</p>
                  <p className="text-xs text-gray-500">Lihat semua wawancara</p>
                </div>
              </div>
              <ArrowRight size={20} className="text-blue-600 group-hover:translate-x-1 transition-transform" />
            </Link>

            <Link
              to="/interviews"
              className="flex items-center justify-between p-4 bg-green-50 hover:bg-green-100 rounded-lg border border-green-200 transition-colors group"
            >
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-green-600 rounded-lg">
                  <TrendingUp size={20} className="text-white" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">Buat Wawancara</p>
                  <p className="text-xs text-gray-500">Mulai wawancara baru</p>
                </div>
              </div>
              <ArrowRight size={20} className="text-green-600 group-hover:translate-x-1 transition-transform" />
            </Link>

            <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg border border-purple-200">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-purple-600 rounded-lg">
                  <Brain size={20} className="text-white" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">AI Success Rate</p>
                  <p className="text-xs text-gray-500">{stats.processing_success_rate}% reliability</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
