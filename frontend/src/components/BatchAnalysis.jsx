
import { useState } from 'react'

function BatchAnalysis() {
  const [file, setFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  
const [currentPage, setCurrentPage] = useState(1)

const itemsPerPage = 10

const totalPages = result
  ? Math.ceil(result.results.length / itemsPerPage)
  : 0

const currentResults = result
  ? result.results.slice(
      (currentPage - 1) * itemsPerPage,
      currentPage * itemsPerPage
    )
  : []


  async function analyzeBatch() {
    if (!file) {
      setError('Please select a CSV file.')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)
    setCurrentPage(1)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(
        'http://127.0.0.1:8000/api/v1/predict/batch',
        {
          method: 'POST',
          body: formData
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          typeof data.detail === 'string'
            ? data.detail
            : JSON.stringify(data.detail)
        )
      }

      setResult(data)

    } catch (err) {
      console.error(err)
      setError(err.message || 'Batch analysis failed.')

    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="history-card">
      <h2>Batch Traffic Analysis</h2>

      <p>
        Upload a CSV file containing network traffic
        records for AI-based classification.
      </p>

      <div className="upload-section">
        <label
          htmlFor="batch-file"
          className="upload-label"
        >
          Upload CSV Dataset
        </label>

        <input
          id="batch-file"
          type="file"
          accept=".csv,text/csv"
          className="file-input"
          onChange={(e) => {
            setFile(e.target.files?.[0] || null)
            setResult(null)
            setError(null)
          }}
        />
      </div>

      <button
        className="analyze-button"
        onClick={analyzeBatch}
        disabled={loading}
      >
        {loading ? 'Analyzing...' : 'Analyze CSV'}
      </button>

      {error && (
        <p className="detection-error">{error}</p>
      )}

      
{result && (
  <div className="batch-results">

    <h3>Batch Analysis Results</h3>

    <div className="batch-stats-grid">

      <div className="batch-stat-card blue">
        <p>Total Analyzed</p>
        <h2>{result.total_analyzed}</h2>
      </div>

      <div className="batch-stat-card green">
        <p>BENIGN Traffic</p>
        <h2>{result.benign_count}</h2>
      </div>

      <div className="batch-stat-card red">
        <p>DDoS Detected</p>
        <h2>{result.ddos_count}</h2>
      </div>

      <div className="batch-stat-card purple">
        <p>DDoS Percentage</p>
        <h2>{result.ddos_percentage}%</h2>
      </div>

    </div>

    
<div className="batch-table-section">

  <h3>Individual Prediction Results</h3>

  <div className="table-wrapper">
    <table className="prediction-table">

      <thead>
        <tr>
          <th>Row</th>
          <th>Prediction</th>
          <th>DDoS Probability</th>
        </tr>
      </thead>

      <tbody>
        {currentResults.map((item) => (
          <tr key={item.row}>

            <td>#{item.row}</td>

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

          </tr>
        ))}
      </tbody>

    </table>
  </div>

<div className="batch-pagination">

  <span>
    Page {currentPage} of {totalPages}
  </span>

  <div className="pagination-buttons">

    <button
      disabled={currentPage === 1}
      onClick={() => setCurrentPage((page) => page - 1)}
    >
      Previous
    </button>

    <button
      disabled={currentPage >= totalPages}
      onClick={() => setCurrentPage((page) => page + 1)}
    >
      Next
    </button>

  </div>
</div>

</div>


  </div>
)}

    </div>
  )
}

export default BatchAnalysis
