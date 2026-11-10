
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'

function PredictionTable() {

  const [predictions, setPredictions] = useState([])
  const [filter, setFilter] = useState('ALL')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

const explainPrediction = (predictionId) => {
  navigate('/ai-assistant', {
    state: {
      predictionId
    }
  })
}
  
useEffect(() => {

  const controller = new AbortController()

  async function fetchPredictions() {
    setLoading(true)
    setError(null)

    try {
      let url = 'http://127.0.0.1:8000/api/v1/predictions?limit=10'

      if (filter !== 'ALL') {
        url += `&prediction=${filter}`
      }

      const response = await fetch(url, {
        signal: controller.signal
      })

      if (!response.ok) {
        throw new Error('Failed to load predictions')
      }

      const result = await response.json()

      setPredictions(result.predictions)

    } catch (err) {
      if (err.name !== 'AbortError') {
        console.error(err)
        setError('Unable to load prediction history.')
      }

    } finally {
      if (!controller.signal.aborted) {
        setLoading(false)
      }
    }
  }

  fetchPredictions()

  return () => controller.abort()

}, [filter])


  return (
    <div className="history-card">

      <h2>Recent AI Predictions</h2>
      <p>Latest network traffic classifications</p>

      
<div className="prediction-filters">

  <button
    className={filter === 'ALL' ? 'selected' : ''}
    onClick={() => setFilter('ALL')}
  >
    All Predictions
  </button>

  <button
    className={filter === 'BENIGN' ? 'selected' : ''}
    onClick={() => setFilter('BENIGN')}
  >
    BENIGN
  </button>

  <button
    className={filter === 'DDoS' ? 'selected' : ''}
    onClick={() => setFilter('DDoS')}
  >
    DDoS
  </button>

</div>


      {loading && <p>Loading predictions...</p>}

      {error && <p>{error}</p>}

      {!loading && !error && predictions.length === 0 && (
        <p>No predictions available.</p>
      )}

      {!loading && !error && predictions.length > 0 && (
        <div className="table-wrapper">
          <table className="prediction-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Prediction</th>
                <th>DDoS Probability</th>
                <th>Date & Time</th>
                <th>Explain with AI</th>
              </tr>
            </thead>

            <tbody>
              {predictions.map((item) => (
                <tr key={item.id}>
                  <td>#{item.id}</td>

                  <td>
                    <span
                      className={
                        item.prediction === 'DDoS'
                          ? 'prediction-badge ddos'
                          : 'prediction-badge benign'
                      }
                    >
                      {item.prediction}
                    </span>
                  </td>

                  <td>
                    {item.ddos_probability_percent}%
                  </td>

                  <td>
                    {new Date(item.created_at).toLocaleString('bs-BA')}
                  </td>
                  <td>
                    <button
                     type="button"
                     className="explain-ai-btn"
                     onClick={() => explainPrediction(item.id)}
                    >
                     Explain with AI
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

    </div>
  )
}

export default PredictionTable
