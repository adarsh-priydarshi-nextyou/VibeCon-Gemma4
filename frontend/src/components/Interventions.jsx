import { useState } from 'react'

function Interventions({ interventions, onRefresh, onTelemetry }) {
  const [playingId, setPlayingId] = useState(null)
  const [playStartTime, setPlayStartTime] = useState(null)

  const handlePlay = (audioId, duration) => {
    setPlayingId(audioId)
    setPlayStartTime(Date.now())
    
    // Simulate audio playback (in real app, use HTML5 Audio API)
    setTimeout(() => {
      const playDuration = (Date.now() - Date.now()) / 1000
      onTelemetry(audioId, playDuration, duration)
      setPlayingId(null)
    }, duration * 1000)
  }

  const handleSkip = (audioId, duration) => {
    const playDuration = playStartTime ? (Date.now() - playStartTime) / 1000 : 0
    onTelemetry(audioId, playDuration, duration)
    setPlayingId(null)
  }

  const handleLike = (audioId, duration, liked) => {
    const playDuration = playStartTime ? (Date.now() - playStartTime) / 1000 : duration
    onTelemetry(audioId, playDuration, duration, liked)
  }

  const getReasonIcon = (reason) => {
    const icons = {
      'high_stress': '🔴',
      'increasing_trend': '📈',
      'sleep_debt': '😴',
      'meeting_overload': '📅',
      'pattern_match': '🎯',
      'user_preference': '⭐'
    }
    return icons[reason] || '💡'
  }

  return (
    <div className="interventions-container">
      <div className="interventions-header">
        <h2>🎧 Recommended Interventions</h2>
        <button className="btn btn-secondary" onClick={onRefresh}>
          🔄 Refresh
        </button>
      </div>

      {interventions.length === 0 ? (
        <div className="card empty-state">
          <p>📭 No interventions available yet</p>
          <p style={{ fontSize: '14px', color: '#718096', marginTop: '10px' }}>
            Record your voice to get personalized recommendations
          </p>
        </div>
      ) : (
        <div className="interventions-list">
          {interventions.map((intervention, index) => (
            <div key={index} className="card intervention-card">
              <div className="intervention-rank">#{index + 1}</div>
              
              <div className="intervention-header">
                <h3>{intervention.audio_title}</h3>
                <div className="intervention-meta">
                  <span className="badge">{intervention.category}</span>
                  <span className="duration">⏱️ {intervention.duration_seconds}s</span>
                </div>
              </div>

              <p className="intervention-description">{intervention.description}</p>

              <div className="intervention-reason">
                <span className="reason-icon">
                  {getReasonIcon(intervention.recommendation_reason)}
                </span>
                <span className="reason-text">
                  {intervention.recommendation_reason.replace('_', ' ')}
                </span>
                <span className="confidence">
                  {Math.round(intervention.confidence_score * 100)}% match
                </span>
              </div>

              <div className="intervention-actions">
                {playingId === intervention.audio_id ? (
                  <>
                    <button 
                      className="btn btn-secondary"
                      onClick={() => handleSkip(intervention.audio_id, intervention.duration_seconds)}
                    >
                      ⏭️ Skip
                    </button>
                    <div className="playing-indicator">
                      <span className="pulse-small"></span>
                      Playing...
                    </div>
                  </>
                ) : (
                  <>
                    <button 
                      className="btn btn-primary"
                      onClick={() => handlePlay(intervention.audio_id, intervention.duration_seconds)}
                    >
                      ▶️ Play
                    </button>
                    <button 
                      className="btn btn-icon"
                      onClick={() => handleLike(intervention.audio_id, intervention.duration_seconds, true)}
                      title="Like"
                    >
                      👍
                    </button>
                    <button 
                      className="btn btn-icon"
                      onClick={() => handleLike(intervention.audio_id, intervention.duration_seconds, false)}
                      title="Dislike"
                    >
                      👎
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Interventions
