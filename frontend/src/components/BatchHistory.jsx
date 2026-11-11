import API_URL from '../config/api'

import { useEffect, useState } from 'react'

function BatchHistory() {

  // Stanja za historiju batch analiza
  const [batches, setBatches] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Stanja za detalje odabrane analize
  const [selectedBatch, setSelectedBatch] = useState(null)
  const [detailsLoading, setDetailsLoading] = useState(false)
  const [detailsError, setDetailsError] = useState(null)

  // Ucitavanje historije batch analiza
  useEffect(() => {
    const controller = new AbortController()

    async function fetchBatchHistory() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/predictions/batches`,
          { signal: controller.signal }
        )

        if (!response.ok) {
          throw new Error('Failed to load batch history')
        }

        const data = await response.json()
        setBatches(data.batches)

      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error(err)
          setError('Unable to load batch history.')
        }

      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    fetchBatchHistory()

    return () => controller.abort()

  }, [])

  // Ucitavanje detalja odabrane batch analize
  async function viewBatchDetails(batchId) {

    setDetailsLoading(true)
    setDetailsError(null)
    setSelectedBatch(null)

    try {
      const response = await fetch(
        `${API_URL}/api/v1/predictions/batches/${batchId}`
      )

      if (!response.ok) {
        throw new Error('Failed to load batch details')
      }

      const data = await response.json()

      setSelectedBatch(data)

    } catch (err) {
      console.error(err)
      setDetailsError('Unable to load batch details.')

    } finally {
      setDetailsLoading(false)
    }
  }

  return (
    <div className="history-card">

      <h2>Batch Analysis History</h2>

      <p>
        Previously analyzed CSV datasets.
      </p>

      {/* Ucitavanje i greske historije */}
      {loading && (
        <p>Loading batch history...</p>
      )}

      {error && (
        <p className="detection-error">{error}</p>
      )}

      {!loading && !error && batches.length === 0 && (
        <p>No batch analyses available.</p>
      )}

      {/* Tabela prethodnih batch analiza */}
      {!loading && !error && batches.length > 0 && (
        <div className="table-wrapper">
          <table className="prediction-table">

            <thead>
              <tr>
                <th>ID</th>
                <th>Filename</th>
                <th>Records</th>
                <th>BENIGN</th>
                <th>DDoS</th>
                <th>Date & Time</th>
                <th>Actions</th>
              </tr>
            </thead>

            <tbody>
              {batches.map((batch) => (
                <tr key={batch.batch_id}>

                  <td>#{batch.batch_id}</td>

                  <td>{batch.filename}</td>

                  <td>{batch.total_analyzed}</td>

                  <td>{batch.benign_count}</td>

                  <td>{batch.ddos_count}</td>

                  <td>
                    {new Date(
                      batch.created_at
                    ).toLocaleString('bs-BA')}
                  </td>

                  <td>
                    <button
                      className="view-details-button"
                      onClick={() =>
                        viewBatchDetails(batch.batch_id)
                      }
                      disabled={detailsLoading}
                    >
                      View Details
                    </button>
                  </td>

                </tr>
              ))}
            </tbody>

          </table>
        </div>
      )}

      {/* Ucitavanje detalja */}
      {detailsLoading && (
        <p>Loading batch details...</p>
      )}

      {detailsError && (
        <p className="detection-error">
          {detailsError}
        </p>
      )}

      {/* Prikaz detalja odabrane analize */}
      {selectedBatch && (
        <div className="batch-details">

          <h3>
            Batch #{selectedBatch.batch_id} – Individual Results
          </h3>

          <p>
            File: {selectedBatch.filename}
          </p>

          <p>
            Total: {selectedBatch.total_analyzed} |
            {' '}BENIGN: {selectedBatch.benign_count} |
            {' '}DDoS: {selectedBatch.ddos_count}
          </p>

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
                {selectedBatch.results.map((item) => (
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

        </div>
      )}

    </div>
  )
}

export default BatchHistory
