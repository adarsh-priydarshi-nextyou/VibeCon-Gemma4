function StressMeter({ score }) {
  const percentage = Math.round(score * 100)
  
  const getStressLevel = () => {
    if (score < 0.3) return { label: 'Low', color: '#48bb78', emoji: '😌' }
    if (score < 0.6) return { label: 'Moderate', color: '#ed8936', emoji: '😐' }
    return { label: 'High', color: '#f56565', emoji: '😰' }
  }

  const level = getStressLevel()

  return (
    <div className="stress-meter">
      <div className="stress-level-header">
        <span className="stress-emoji">{level.emoji}</span>
        <div>
          <div className="stress-label">{level.label} Stress</div>
          <div className="stress-percentage">{percentage}%</div>
        </div>
      </div>

      <div className="stress-bar-container">
        <div 
          className="stress-bar"
          style={{ 
            width: `${percentage}%`,
            backgroundColor: level.color
          }}
        >
          <div className="stress-bar-shine"></div>
        </div>
      </div>

      <div className="stress-scale">
        <span>0%</span>
        <span>Low</span>
        <span>Moderate</span>
        <span>High</span>
        <span>100%</span>
      </div>
    </div>
  )
}

export default StressMeter
