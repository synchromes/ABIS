import { Link } from 'react-router-dom'
import { Home, AlertCircle } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <AlertCircle size={64} className="mx-auto text-gray-400 mb-4" />
        <h1 className="text-6xl font-bold text-gray-900 mb-2">404</h1>
        <p className="text-xl text-gray-600 mb-8">Halaman tidak ditemukan</p>
        <Link to="/" className="btn btn-primary inline-flex items-center space-x-2">
          <Home size={20} />
          <span>Kembali ke Dashboard</span>
        </Link>
      </div>
    </div>
  )
}
