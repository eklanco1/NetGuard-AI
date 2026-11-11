import API_URL from '../config/api'

import { useEffect, useState } from 'react'

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts'

function BatchComparisonChart() {

  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()

    async function fetchBatchComparison() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/predictions/batches/stats`,
          { signal: controller.signal }
        )

        if (!response.ok) {
          throw new Error('Failed to load batch comparison')
        }

        const stats = await response.json()

        setData([
          {
            name: 'BENIGN',
            count: stats.benign_records
          },
          {
            name: 'DDoS',
            count: stats.ddos_records
          }
        ])

      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error(err)
          setError('Unable to load batch comparison.')
        }

      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    fetchBatchComparison()

    return () => controller.abort()
  }, [])

  const colors = ['#22c55e', '#f87171']
  const total = data.reduce((sum, item) => sum + item.count, 0)

  return (
    <div className="history-card">

      <h2>Batch Classification Comparison</h2>

      <p>
        Comparison of BENIGN and DDoS classifications
        across saved batch analyses.
      </p>

      {loading && <p>Loading comparison...</p>}

      {error && (
        <p className="detection-error">{error}</p>
      )}

      {!loading && !error && total === 0 && (
        <p>No batch prediction data available.</p>
      )}

      {!loading && !error && total > 0 && (
        <div className="batch-chart-container">

          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid
                stroke="#26354b"
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="name"
                stroke="#94a3b8"
              />

              <YAxis
                stroke="#94a3b8"
                allowDecimals={false}
              />

              <Tooltip />

              <Bar
                dataKey="count"
                name="Predictions"
                radius={[6, 6, 0, 0]}
              >
                {data.map((item, index) => (
                  <Cell
                    key={item.name}
                    fill={colors[index]}
                  />
                ))}
              </Bar>

            </BarChart>
          </ResponsiveContainer>

        </div>
      )}

    </div>
  )
}

export default BatchComparisonChart
