import { useEffect, useRef } from 'react'
import { MessageCircle } from 'lucide-react'

export default function TranscriptPanel({ entries }) {
  const scrollRef = useRef(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [entries])

  const formatTimestamp = (timestamp) => {
    const minutes = Math.floor(timestamp / 60)
    const seconds = Math.floor(timestamp % 60)
    return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <div ref={scrollRef} className="h-96 overflow-y-auto space-y-4 pr-2">
      {entries.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-gray-400">
          <MessageCircle size={48} className="mb-3" />
          <p>Transkrip akan muncul di sini</p>
          <p className="text-sm">saat wawancara dimulai</p>
        </div>
      ) : (
        entries.map((entry, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium text-sm text-primary-600">
                {entry.speaker}
              </span>
              <span className="text-xs text-gray-500">
                {formatTimestamp(entry.timestamp)}
              </span>
            </div>
            <p className="text-gray-800 text-sm leading-relaxed">{entry.text}</p>
            {entry.confidence !== undefined && (
              <div className="mt-2 flex items-center space-x-2">
                <div className="flex-1 bg-gray-200 rounded-full h-1">
                  <div
                    className="bg-green-500 h-1 rounded-full"
                    style={{ width: `${entry.confidence * 100}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-500">
                  {(entry.confidence * 100).toFixed(0)}%
                </span>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  )
}
