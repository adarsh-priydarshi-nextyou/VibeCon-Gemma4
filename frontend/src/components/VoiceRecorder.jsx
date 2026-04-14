import { useState, useRef } from 'react'

function VoiceRecorder({ onAudioProcessed, loading }) {
  const [isRecording, setIsRecording] = useState(false)
  const [recordingTime, setRecordingTime] = useState(0)
  const mediaRecorderRef = useRef(null)
  const chunksRef = useRef([])
  const timerRef = useRef(null)

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      
      // Try to use WAV format if supported, otherwise use WebM
      let options = { mimeType: 'audio/webm' }
      if (MediaRecorder.isTypeSupported('audio/wav')) {
        options = { mimeType: 'audio/wav' }
      } else if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
        options = { mimeType: 'audio/webm;codecs=opus' }
      }
      
      mediaRecorderRef.current = new MediaRecorder(stream, options)
      chunksRef.current = []

      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          chunksRef.current.push(e.data)
        }
      }

      mediaRecorderRef.current.onstop = async () => {
        const mimeType = mediaRecorderRef.current.mimeType
        const audioBlob = new Blob(chunksRef.current, { type: mimeType })
        
        // Convert to WAV using Web Audio API
        try {
          const audioContext = new (window.AudioContext || window.webkitAudioContext)()
          const arrayBuffer = await audioBlob.arrayBuffer()
          const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
          
          // Convert to WAV format
          const wavBlob = await audioBufferToWav(audioBuffer)
          onAudioProcessed(wavBlob)
        } catch (err) {
          console.error('Audio conversion failed:', err)
          // Fallback: send original blob
          onAudioProcessed(audioBlob)
        }
        
        // Stop all tracks
        stream.getTracks().forEach(track => track.stop())
      }

      mediaRecorderRef.current.start()
      setIsRecording(true)
      setRecordingTime(0)

      // Start timer
      timerRef.current = setInterval(() => {
        setRecordingTime(prev => prev + 1)
      }, 1000)

    } catch (err) {
      console.error('Failed to start recording:', err)
      alert('Failed to access microphone. Please grant permission.')
    }
  }

  // Convert AudioBuffer to WAV blob
  const audioBufferToWav = (audioBuffer) => {
    return new Promise((resolve) => {
      const numberOfChannels = audioBuffer.numberOfChannels
      const sampleRate = audioBuffer.sampleRate
      const format = 1 // PCM
      const bitDepth = 16
      
      const bytesPerSample = bitDepth / 8
      const blockAlign = numberOfChannels * bytesPerSample
      
      const data = []
      for (let i = 0; i < audioBuffer.numberOfChannels; i++) {
        data.push(audioBuffer.getChannelData(i))
      }
      
      const interleaved = interleave(data)
      const dataLength = interleaved.length * bytesPerSample
      const buffer = new ArrayBuffer(44 + dataLength)
      const view = new DataView(buffer)
      
      // Write WAV header
      writeString(view, 0, 'RIFF')
      view.setUint32(4, 36 + dataLength, true)
      writeString(view, 8, 'WAVE')
      writeString(view, 12, 'fmt ')
      view.setUint32(16, 16, true)
      view.setUint16(20, format, true)
      view.setUint16(22, numberOfChannels, true)
      view.setUint32(24, sampleRate, true)
      view.setUint32(28, sampleRate * blockAlign, true)
      view.setUint16(32, blockAlign, true)
      view.setUint16(34, bitDepth, true)
      writeString(view, 36, 'data')
      view.setUint32(40, dataLength, true)
      
      // Write audio data
      floatTo16BitPCM(view, 44, interleaved)
      
      resolve(new Blob([buffer], { type: 'audio/wav' }))
    })
  }

  const interleave = (channelData) => {
    const length = channelData[0].length
    const numberOfChannels = channelData.length
    const result = new Float32Array(length * numberOfChannels)
    
    let offset = 0
    for (let i = 0; i < length; i++) {
      for (let channel = 0; channel < numberOfChannels; channel++) {
        result[offset++] = channelData[channel][i]
      }
    }
    return result
  }

  const writeString = (view, offset, string) => {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i))
    }
  }

  const floatTo16BitPCM = (view, offset, input) => {
    for (let i = 0; i < input.length; i++, offset += 2) {
      const s = Math.max(-1, Math.min(1, input[i]))
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop()
      setIsRecording(false)
      
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="voice-recorder">
      <div className="recorder-controls">
        {!isRecording ? (
          <button 
            className="btn btn-primary btn-large"
            onClick={startRecording}
            disabled={loading}
          >
            {loading ? '⏳ Processing...' : '🎤 Start Recording'}
          </button>
        ) : (
          <div className="recording-active">
            <div className="recording-indicator">
              <span className="pulse"></span>
              <span className="recording-text">Recording...</span>
            </div>
            <div className="recording-time">{formatTime(recordingTime)}</div>
            <button 
              className="btn btn-danger btn-large"
              onClick={stopRecording}
            >
              ⏹️ Stop Recording
            </button>
          </div>
        )}
      </div>

      <div className="recorder-info">
        <p>💡 Speak naturally for 10-30 seconds for best results</p>
        <p>🔒 All processing happens locally on your device</p>
      </div>
    </div>
  )
}

export default VoiceRecorder
