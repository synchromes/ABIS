import { Radar, RadarChart as RechartsRadar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer } from 'recharts'

export default function RadarChart({ scores }) {
  const dimensions = [
    { key: 'berorientasi_pelayanan', label: 'Berorientasi Pelayanan' },
    { key: 'akuntabel', label: 'Akuntabel' },
    { key: 'kompeten', label: 'Kompeten' },
    { key: 'harmonis', label: 'Harmonis' },
    { key: 'loyal', label: 'Loyal' },
    { key: 'adaptif', label: 'Adaptif' },
    { key: 'kolaboratif', label: 'Kolaboratif' },
  ]

  const data = dimensions.map(dim => ({
    dimension: dim.label.split(' ').slice(0, 2).join(' '),
    value: scores[dim.key] || 0,
    fullMark: 5,
  }))

  const hasData = Object.keys(scores).length > 0

  if (!hasData) {
    return (
      <div className="h-64 flex items-center justify-center text-gray-400">
        <div className="text-center">
          <p>Belum ada data</p>
          <p className="text-sm">Mulai wawancara untuk melihat analisis</p>
        </div>
      </div>
    )
  }

  return (
    <ResponsiveContainer width="100%" height={300}>
      <RechartsRadar data={data}>
        <PolarGrid stroke="#e5e7eb" />
        <PolarAngleAxis 
          dataKey="dimension" 
          tick={{ fill: '#6b7280', fontSize: 11 }}
        />
        <PolarRadiusAxis 
          angle={90} 
          domain={[0, 5]}
          tick={{ fill: '#9ca3af', fontSize: 10 }}
        />
        <Radar 
          name="Nilai" 
          dataKey="value" 
          stroke="#3b82f6" 
          fill="#3b82f6" 
          fillOpacity={0.6} 
        />
      </RechartsRadar>
    </ResponsiveContainer>
  )
}
