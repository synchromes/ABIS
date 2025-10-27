import config from '../config'

class WebSocketService {
  constructor() {
    this.ws = null
    this.interviewId = null
    this.listeners = new Map()
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
  }

  connect(interviewId) {
    return new Promise((resolve, reject) => {
      this.interviewId = interviewId
      const wsUrl = `${config.wsBaseUrl}/ws/interview/${interviewId}`

      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        resolve()
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          this.handleMessage(message)
        } catch (error) {
          console.error('Error parsing message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        reject(error)
      }

      this.ws.onclose = () => {
        console.log('WebSocket closed')
        this.handleReconnect()
      }
    })
  }

  handleMessage(message) {
    const { type, data } = message
    const listeners = this.listeners.get(type) || []
    listeners.forEach(callback => callback(data))
  }

  on(type, callback) {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, [])
    }
    this.listeners.get(type).push(callback)
  }

  off(type, callback) {
    const listeners = this.listeners.get(type)
    if (listeners) {
      const index = listeners.indexOf(callback)
      if (index > -1) {
        listeners.splice(index, 1)
      }
    }
  }

  send(type, data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const message = { type, data }
      console.log(`[WS] Sending message type: ${type}`)
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn(`[WS] Cannot send ${type}, WebSocket not open`)
    }
  }

  sendVideoFrame(frameData) {
    this.send('video_frame', frameData)
  }

  sendAudioChunk(audioData) {
    this.send('audio_chunk', audioData)
  }

  saveTranscript(transcriptData) {
    this.send('save_transcript', transcriptData)
  }

  saveEmotion(emotionData) {
    this.send('save_emotion', emotionData)
  }

  getAnalysis() {
    this.send('get_analysis', {})
  }

  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)
      setTimeout(() => {
        if (this.interviewId) {
          this.connect(this.interviewId).catch(console.error)
        }
      }, 2000 * this.reconnectAttempts)
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.listeners.clear()
    this.interviewId = null
    this.reconnectAttempts = 0
  }
}

export default new WebSocketService()
