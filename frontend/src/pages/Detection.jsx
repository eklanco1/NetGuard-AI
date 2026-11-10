import BatchAnalysis from '../components/BatchAnalysis'
import { useState } from 'react'
import BatchHistory from '../components/BatchHistory'

function Detection() {

  const [jsonInput, setJsonInput] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  
async function handleFileUpload(event) {
  const file = event.target.files?.[0]

  if (!file) {
    return
  }

  setError(null)
  setResult(null)

  if (!file.name.toLowerCase().endsWith('.json')) {
    setError('Please select a JSON file.')
    event.target.value = ''
    return
  }

  try {
    const fileContent = await file.text()

    const parsedData = JSON.parse(fileContent)

    if (
      !parsedData ||
      typeof parsedData !== 'object' ||
      Array.isArray(parsedData) ||
      !parsedData.features ||
      typeof parsedData.features !== 'object' ||
      Array.isArray(parsedData.features)
    ) {
      throw new Error(
        'JSON must contain a features object.'
      )
    }

    setJsonInput(JSON.stringify(parsedData, null, 2))

  } catch (err) {
    setError(err.message || 'Unable to read JSON file.')
  }

  event.target.value = ''
}


  async function analyzeTraffic() {

    setError(null)
    setResult(null)

    let inputData

    // Provjera JSON formata
    try {
      inputData = JSON.parse(jsonInput)
    } catch {
      setError('Invalid JSON format.')
      return
    }

    // Provjera osnovne strukture
    if (
      !inputData ||
      typeof inputData !== 'object' ||
      Array.isArray(inputData) ||
      !inputData.features ||
      typeof inputData.features !== 'object' ||
      Array.isArray(inputData.features)
    ) {
      setError('JSON must contain a features object.')
      return
    }

    setLoading(true)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/api/v1/predict',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(inputData)
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(JSON.stringify(data.detail))
      }

      setResult(data)

    } catch (err) {
      console.error(err)
      setError(err.message || 'AI prediction failed.')

    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <h1>AI Threat Detection</h1>

      <p>
        Analyze network traffic using our trained AI model.
      </p>

      <div className="history-card">

        <h2>Network Traffic Analysis</h2>

        <p>
          Enter network traffic features in JSON format.
        </p>

        <textarea
        
          className="json-input"
          placeholder='{"features": { ... }}'
          value={jsonInput}
          onChange={(e) => setJsonInput(e.target.value)}
          rows={12}
        />

        
<div className="upload-section">
  <label
    htmlFor="traffic-file"
    className="upload-label"
  >
    Upload JSON Sample
  </label>

  <input
    id="traffic-file"
    type="file"
    accept=".json,application/json"
    onChange={handleFileUpload}
    className="file-input"
  />

  <p className="upload-description">
    Select a JSON file containing network traffic features.
  </p>
</div>


        <button
          className="analyze-button"
          onClick={analyzeTraffic}
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Analyze Traffic'}
        </button>

        {error && (
          <p className="detection-error">{error}</p>
        )}

        
{result && (
  <div
    className={`detection-result ${
      result.prediction === 'DDoS' ? 'threat' : 'safe'
    }`}
  >
    <h3>AI Prediction Result</h3>

    <div className="result-header">
      <span className="result-icon">
        {result.prediction === 'DDoS' ? '⚠' : '✓'}
      </span>

      <div>
        <p className="result-label">
          Network Traffic Classification
        </p>

        <h2>
          {result.prediction === 'DDoS'
            ? 'DDoS Detected'
            : 'BENIGN Traffic'}
        </h2>
      </div>
    </div>

    <div className="probability-header">
      <span>DDoS Probability</span>
      <strong>{result.ddos_probability_percent}%</strong>
    </div>

    <div className="probability-track">
      <div
        className="probability-fill"
        style={{
          width: `${Math.max(
            0,
            Math.min(100, result.ddos_probability_percent)
          )}%`
        }}
      />
    </div>

    <p className="result-id">
      Prediction ID: #{result.prediction_id}
    </p>
  </div>
)}


      </div>

      <BatchAnalysis />
      <BatchHistory />
    </>
  )
}

export default Detection
