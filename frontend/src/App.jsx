import { useState, useEffect } from 'react'
import axios from 'axios'
import VoiceRecorder from './components/VoiceRecorder'
import StressMeter from './components/StressMeter'
import Insights from './components/Insights'
import Interventions from './components/Interventions'
import './App.css'

const API_BASE = 'http://localhost:8000'

// Get or create device ID (persistent across sessions)
const getDeviceId = () => {
  let deviceId = localStorage.getItem('device_id');
  if (!deviceId) {
    // Generate device ID from browser fingerprint
    const fingerprint = [
      navigator.userAgent,
      navigator.language,
      screen.width + 'x' + screen.height,
      new Date().getTimezoneOffset()
    ].join('|');
    
    // Create hash
    const hash = fingerprint.split('').reduce((acc, char) => {
      return ((acc << 5) - acc) + char.charCodeAt(0);
    }, 0);
    
    deviceId = `device_${Math.abs(hash).toString(16).padStart(16, '0').substring(0, 16)}`;
    localStorage.setItem('device_id', deviceId);
    console.log('Created new device ID:', deviceId);
  }
  return deviceId;
};

const USER_ID = getDeviceId();

function App() {
  const [activeTab, setActiveTab] = useState('record')
  const [stressScore, setStressScore] = useState(null)
  const [insights, setInsights] = useState([])
  const [interventions, setInterventions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [stats, setStats] = useState({
    totalRecordings: 0,
    avgStress: 0,
    trend: 'stable'
  })

  // Auto-dismiss alerts after 5 seconds
  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null)
        setSuccess(null)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [error, success])

  // Fetch insights
  const fetchInsights = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/insights/${USER_ID}`)
      setInsights(response.data)
    } catch (err) {
      console.error('Failed to fetch insights:', err)
    }
  }

  // Fetch interventions
  const fetchInterventions = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/interventions/${USER_ID}`)
      setInterventions(response.data)
    } catch (err) {
      console.error('Failed to fetch interventions:', err)
    }
  }

  // Fetch user stats
  const fetchStats = async () => {
    try {
      // This would be a real API call in production
      // For now, calculate from insights
      if (insights.length > 0) {
        const pattern = insights[0].stress_pattern
        setStats(prev => ({
          ...prev,
          trend: pattern
        }))
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err)
    }
  }

  // Handle audio processing
  const handleAudioProcessed = async (audioBlob) => {
    setLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'recording.wav')

      const response = await axios.post(`${API_BASE}/api/audio/process`, formData, {
        headers: {
          'X-User-ID': USER_ID,
          'Content-Type': 'multipart/form-data'
        }
      })

      setStressScore(response.data.stress_score)
      setSuccess('✓ Voice analysis complete! Check your stress level below.')
      
      // Update stats
      setStats(prev => ({
        totalRecordings: prev.totalRecordings + 1,
        avgStress: prev.avgStress === 0 ? response.data.stress_score : 
                   (prev.avgStress + response.data.stress_score) / 2,
        trend: prev.trend
      }))
      
      // Fetch updated insights and interventions
      setTimeout(() => {
        fetchInsights()
        fetchInterventions()
        fetchStats()
      }, 1000)

    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Failed to process audio. Please try again.'
      setError(errorMsg)
      console.error('Audio processing error:', err)
    } finally {
      setLoading(false)
    }
  }

  // Record telemetry
  const recordTelemetry = async (audioId, playDuration, totalDuration, liked = null) => {
    try {
      const telemetryData = {
        audio_id: audioId,
        audio_url: `https://example.com/audio/${audioId}.mp3`,
        play_duration_seconds: playDuration,
        total_duration_seconds: totalDuration,
        stress_score_at_interaction: stressScore || 0.5,
        session_id: `session-${Date.now()}`,
        device_platform: 'Web',
        app_version: '1.0.0'
      }

      if (liked !== null) {
        await axios.post(`${API_BASE}/api/telemetry/feedback`, {
          ...telemetryData,
          like_status: liked,
          feedback_text: null
        }, {
          headers: { 'X-User-ID': USER_ID }
        })
      } else {
        await axios.post(`${API_BASE}/api/telemetry/play`, telemetryData, {
          headers: { 'X-User-ID': USER_ID }
        })
      }
    } catch (err) {
      console.error('Failed to record telemetry:', err)
    }
  }

  useEffect(() => {
    // Initial data fetch
    fetchInsights()
    fetchInterventions()
  }, [])

  return (
    <div className="app">
      <header className="app-header">
        <div className="container">
          <div className="header-content">
            <div className="header-text">
              <h1>🎙️ Voice Analysis & Intervention System</h1>
              <p>AI-powered stress detection and personalized wellness recommendations</p>
            </div>
            <div className="header-stats">
              <div className="stat-card">
                <div className="stat-value">{stats.totalRecordings}</div>
                <div className="stat-label">Recordings</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">{Math.round(stats.avgStress * 100)}%</div>
                <div className="stat-label">Avg Stress</div>
              </div>
              <div className="stat-card">
                <div className="stat-value">
                  {stats.trend === 'increasing' ? '📈' : 
                   stats.trend === 'decreasing' ? '📉' : '➡️'}
                </div>
                <div className="stat-label">Trend</div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container">
        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">⚠️</span>
            <span className="alert-message">{error}</span>
            <button className="alert-close" onClick={() => setError(null)}>×</button>
          </div>
        )}
        
        {success && (
          <div className="alert alert-success">
            <span className="alert-icon">✓</span>
            <span className="alert-message">{success}</span>
            <button className="alert-close" onClick={() => setSuccess(null)}>×</button>
          </div>
        )}

        <div className="tabs">
          <button 
            className={`tab ${activeTab === 'record' ? 'active' : ''}`}
            onClick={() => setActiveTab('record')}
          >
            <span className="tab-icon">🎤</span>
            <span className="tab-text">Record</span>
          </button>
          <button 
            className={`tab ${activeTab === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveTab('insights')}
          >
            <span className="tab-icon">📊</span>
            <span className="tab-text">Insights</span>
            {insights.length > 0 && <span className="tab-badge">{insights.length}</span>}
          </button>
          <button 
            className={`tab ${activeTab === 'interventions' ? 'active' : ''}`}
            onClick={() => setActiveTab('interventions')}
          >
            <span className="tab-icon">🎧</span>
            <span className="tab-text">Interventions</span>
            {interventions.length > 0 && <span className="tab-badge">{interventions.length}</span>}
          </button>
        </div>

        {activeTab === 'record' && (
          <div className="tab-content">
            <div className="card card-primary">
              <div className="card-header">
                <h2>Voice Recording</h2>
                <p>Record your voice to analyze stress levels using AI</p>
              </div>
              <VoiceRecorder 
                onAudioProcessed={handleAudioProcessed}
                loading={loading}
              />
            </div>

            {stressScore !== null && (
              <div className="card card-result">
                <div className="card-header">
                  <h2>Your Stress Level</h2>
                  <p>Based on voice analysis</p>
                </div>
                <StressMeter score={stressScore} />
              </div>
            )}
          </div>
        )}

        {activeTab === 'insights' && (
          <div className="tab-content">
            <Insights insights={insights} onRefresh={fetchInsights} />
          </div>
        )}

        {activeTab === 'interventions' && (
          <div className="tab-content">
            <Interventions 
              interventions={interventions}
              onRefresh={fetchInterventions}
              onTelemetry={recordTelemetry}
            />
          </div>
        )}
      </div>

      <footer className="app-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-info">
              <p className="footer-title">Voice Analysis & Intervention System v1.0.0</p>
              <p className="footer-subtitle">Privacy-first AI-powered wellness platform</p>
            </div>
            <div className="footer-meta">
              <p className="footer-user">User ID: {USER_ID}</p>
              <p className="footer-privacy">🔒 All processing happens locally</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
