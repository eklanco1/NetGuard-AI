import API_URL from '../config/api'

import { useEffect, useState } from 'react'

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

function TrafficDistribution() {

  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()

    async function fetchDistribution() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/predictions/stats`,
          { signal: controller.signal }
        )

        if (!response.ok) {
          throw new Error('Failed to load statistics')
        }

        const stats = await response.json()

        setData([
          {
            name: 'BENIGN',
            value: stats.benign_predictions
          },
          {
            name: 'DDoS',
            value: stats.ddos_predictions
          }
        ])

      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error(err)
          setError('Unable to load traffic distribution.')
        }

      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    fetchDistribution()

    return () => controller.abort()

  }, [])

  const colors = ['#22c55e', '#f87171']
  const total = data.reduce((sum, item) => sum + item.value, 0)

  return (
    <div className="history-card">

      <h2>Traffic Classification Distribution</h2>

      <p>
        Distribution of BENIGN and DDoS AI predictions.
      </p>

      {loading && <p>Loading distribution...</p>}

      {error && <p className="detection-error">{error}</p>}

      {!loading && !error && total === 0 && (
        <p>No prediction data available.</p>
      )}

      {!loading && !error && total > 0 && (
        <div className="distribution-chart">

          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                innerRadius={75}
                outerRadius={115}
                paddingAngle={3}
              >
                {data.map((entry, index) => (
                  <Cell
                    key={entry.name}
                    fill={colors[index]}
                  />
                ))}
              </Pie>

              <Tooltip />

              <Legend />

            </PieChart>
          </ResponsiveContainer>

        </div>
      )}

    </div>
  )
}

export default TrafficDistribution
