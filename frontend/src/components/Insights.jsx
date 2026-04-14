function Insights({ insights, onRefresh }) {
  const formatDate = (dateStr) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const getPatternIcon = (pattern) => {
    const icons = {
      'increasing': '📈',
      'decreasing': '📉',
      'stable': '➡️',
      'volatile': '📊',
      'improving': '✅',
      'concerning': '⚠️'
    }
    return icons[pattern] || '📊'
  }

  return (
    <div className="insights-container">
      <div className="insights-header">
        <h2>📊 Your Insights</h2>
        <button className="btn btn-secondary" onClick={onRefresh}>
          🔄 Refresh
        </button>
      </div>

      {insights.length === 0 ? (
        <div className="card empty-state">
          <p>📭 No insights available yet</p>
          <p style={{ fontSize: '14px', color: '#718096', marginTop: '10px' }}>
            Record your voice to generate personalized insights
          </p>
        </div>
      ) : (
        <div className="insights-list">
          {insights.map((insight, index) => (
            <div key={index} className="card insight-card">
              <div className="insight-header">
                <span className="insight-icon">
                  {getPatternIcon(insight.stress_pattern)}
                </span>
                <div>
                  <h3>{insight.stress_pattern.replace('_', ' ').toUpperCase()}</h3>
                  <p className="insight-date">
                    {formatDate(insight.generation_date)}
                  </p>
                </div>
              </div>

              <div className="insight-section">
                <h4>Pattern Description</h4>
                <p>{insight.pattern_description}</p>
              </div>

              {insight.contributing_factors && insight.contributing_factors.length > 0 && (
                <div className="insight-section">
                  <h4>Contributing Factors</h4>
                  <ul className="factor-list">
                    {insight.contributing_factors.map((factor, i) => (
                      <li key={i}>{factor}</li>
                    ))}
                  </ul>
                </div>
              )}

              {insight.observations && insight.observations.length > 0 && (
                <div className="insight-section">
                  <h4>Observations</h4>
                  <ul className="observation-list">
                    {insight.observations.map((obs, i) => (
                      <li key={i}>{obs}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default Insights
