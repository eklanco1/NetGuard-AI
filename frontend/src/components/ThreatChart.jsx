
import { useEffect, useState } from 'react'

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'

function ThreatChart() {

  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {

    async function fetchTimeline() {
      try {
        const response = await fetch(
          'http://127.0.0.1:8000/api/v1/predictions/timeline'
        )

        if (!response.ok) {
          throw new Error('Failed to load timeline')
        }

        const result = await response.json()

        const formattedData = result.timeline.map((item) => ({
          hour: new Date(item.hour).toLocaleString('bs-BA', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          }),
          benign: item.benign_count,
          ddos: item.ddos_count
        }))

        setData(formattedData)

      } catch (err) {
        console.error(err)
        setError('Unable to load threat activity.')

      } finally {
        setLoading(false)
      }
    }

    fetchTimeline()

  }, [])

  return (
    <div className="chart-card">

      <h2>Network Threat Activity</h2>
      <p>AI predictions over time</p>

      {loading && <p>Loading chart...</p>}

      {error && <p>{error}</p>}

      {!loading && !error && data.length === 0 && (
        <p>No prediction history available.</p>
      )}

      {!loading && !error && data.length > 0 && (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid
                stroke="#26354b"
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="hour"
                stroke="#94a3b8"
                tick={{ fontSize: 12 }}
              />

              <YAxis
                stroke="#94a3b8"
                allowDecimals={false}
              />

              <Tooltip />

              <Legend />

              <Line
                type="monotone"
                dataKey="benign"
                name="BENIGN"
                stroke="#22c55e"
                strokeWidth={3}
                dot={{ r: 5, fill: "#22c55e" }}
                activeDot={{ r: 8 }}
              />

              <Line
                type="monotone"
                dataKey="ddos"
                name="DDoS"
                stroke="#f87171"
                strokeWidth={3}
                dot={{ r: 5, fill: "#f87171" }}
                activeDot={{ r: 8 }}
              />

            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

    </div>
  )
}

export default ThreatChart
