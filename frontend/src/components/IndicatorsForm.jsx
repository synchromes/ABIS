import { useState } from 'react'
import { Plus, X, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function IndicatorsForm({ indicators, onChange }) {
  const [newIndicator, setNewIndicator] = useState({
    name: '',
    description: '',
    weight: 1.0
  })

  const addIndicator = () => {
    if (!newIndicator.name.trim()) {
      toast.error('Nama indikator harus diisi')
      return
    }

    onChange([...indicators, { ...newIndicator, tempId: Date.now() }])
    setNewIndicator({ name: '', description: '', weight: 1.0 })
    toast.success('Indikator ditambahkan')
  }

  const removeIndicator = (tempId) => {
    onChange(indicators.filter(ind => ind.tempId !== tempId))
  }

  const updateIndicator = (tempId, field, value) => {
    onChange(
      indicators.map(ind =>
        ind.tempId === tempId ? { ...ind, [field]: value } : ind
      )
    )
  }

  const defaultIndicators = [
    { name: 'Komunikasi', description: 'Kemampuan berkomunikasi dengan jelas dan efektif', weight: 1.5 },
    { name: 'Kepemimpinan', description: 'Kemampuan memimpin tim dan mengambil keputusan', weight: 1.0 },
    { name: 'Problem Solving', description: 'Kemampuan menganalisis dan menyelesaikan masalah', weight: 2.0 },
    { name: 'Teamwork', description: 'Kemampuan bekerja sama dalam tim', weight: 1.0 },
    { name: 'Adaptabilitas', description: 'Kemampuan beradaptasi dengan perubahan', weight: 1.0 },
  ]

  const loadDefaults = () => {
    const withIds = defaultIndicators.map(ind => ({ ...ind, tempId: Date.now() + Math.random() }))
    onChange(withIds)
    toast.success('Indikator default dimuat')
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Indicators
          </label>
          <p className="text-sm text-gray-500">
            Tambahkan indikator khusus untuk menilai kandidat (minimal 1 indikator)
          </p>
        </div>
        <button
          type="button"
          onClick={loadDefaults}
          className="btn btn-outline btn-sm"
        >
          Load Defaults
        </button>
      </div>

      {/* List of existing indicators */}
      {indicators.length > 0 && (
        <div className="space-y-2 max-h-60 overflow-y-auto border rounded-lg p-3">
          {indicators.map((indicator) => (
            <div
              key={indicator.tempId}
              className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg border"
            >
              <div className="flex-1 space-y-2">
                <input
                  type="text"
                  value={indicator.name}
                  onChange={(e) => updateIndicator(indicator.tempId, 'name', e.target.value)}
                  placeholder="Nama indikator"
                  className="input input-sm w-full"
                />
                <input
                  type="text"
                  value={indicator.description}
                  onChange={(e) => updateIndicator(indicator.tempId, 'description', e.target.value)}
                  placeholder="Deskripsi (opsional)"
                  className="input input-sm w-full"
                />
                <div className="flex items-center gap-2">
                  <label className="text-sm text-gray-600">Bobot:</label>
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    max="10"
                    value={indicator.weight}
                    onChange={(e) => updateIndicator(indicator.tempId, 'weight', parseFloat(e.target.value))}
                    className="input input-sm w-20"
                  />
                </div>
              </div>
              <button
                type="button"
                onClick={() => removeIndicator(indicator.tempId)}
                className="btn btn-ghost btn-sm text-red-500 hover:bg-red-50"
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Add new indicator form */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-4 space-y-3">
        <input
          type="text"
          value={newIndicator.name}
          onChange={(e) => setNewIndicator({ ...newIndicator, name: e.target.value })}
          placeholder="Nama indikator (contoh: Komunikasi)"
          className="input w-full"
          onKeyPress={(e) => e.key === 'Enter' && addIndicator()}
        />
        <input
          type="text"
          value={newIndicator.description}
          onChange={(e) => setNewIndicator({ ...newIndicator, description: e.target.value })}
          placeholder="Deskripsi (opsional)"
          className="input w-full"
        />
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <label className="text-sm text-gray-600">Bobot:</label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              max="10"
              value={newIndicator.weight}
              onChange={(e) => setNewIndicator({ ...newIndicator, weight: parseFloat(e.target.value) })}
              className="input input-sm w-24"
            />
          </div>
          <button
            type="button"
            onClick={addIndicator}
            className="btn btn-primary btn-sm flex items-center gap-2"
          >
            <Plus size={16} />
            Tambah Indikator
          </button>
        </div>
      </div>

      {indicators.length === 0 && (
        <div className="text-center py-4 text-gray-500 text-sm">
          Belum ada indikator. Tambahkan minimal 1 indikator atau load defaults.
        </div>
      )}

      <div className="flex items-start gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <div className="text-blue-600 text-sm">
          <strong>ℹ️ Info:</strong> Indikator akan digunakan untuk menganalisis transkrip wawancara.
          Bobot menentukan pengaruh indikator terhadap skor akhir (default: 1.0).
        </div>
      </div>
    </div>
  )
}
