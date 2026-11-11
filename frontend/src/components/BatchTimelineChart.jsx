import API_URL from '../config/api'

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

function BatchTimelineChart() {

  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [period, setPeriod] = useState('7')

  // FETCH BATCH TIMELINE DATA
  useEffect(() => {
    const controller = new AbortController()

    async function fetchBatchTimeline() {
      setLoading(true)
      setError(null)

      try {
        let url =
          `${API_URL}/api/v1/predictions/batches/timeline`

        if (period !== 'all') {
          url += `?days=${period}`
        }

        const response = await fetch(url, {
          signal: controller.signal
        })

        if (!response.ok) {
          throw new Error('Failed to load batch timeline')
        }

        const result = await response.json()

        const formattedData = result.timeline.map((item) => ({
          day: item.day.split('-').reverse().join('.'),
          benign: item.benign_count,
          ddos: item.ddos_count,
          total: item.total_records,
          batches: item.total_batches
        }))

        setData(formattedData)

      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error(err)
          setError('Unable to load batch activity.')
        }

      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    fetchBatchTimeline()

    return () => controller.abort()

  }, [period])


  // EXPORT TIMELINE DATA TO CSV
  const exportToCSV = () => {
    if (loading || error || data.length === 0) return

    const headers = [
      'Date',
      'Total Batches',
      'Total Records',
      'BENIGN',
      'DDoS'
    ]

    const rows = data.map((item) => [
      item.day,
      item.batches,
      item.total,
      item.benign,
      item.ddos
    ])

    const csvContent = [
      headers.join(','),
      ...rows.map((row) => row.join(','))
    ].join('\r\n')

    const blob = new Blob(
      ['\uFEFF' + csvContent],
      { type: 'text/csv;charset=utf-8;' }
    )

    const url = URL.createObjectURL(blob)

    const link = document.createElement('a')
    link.href = url
    link.download = `netguard_batch_analytics_${period}.csv`

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    URL.revokeObjectURL(url)
  }


  return (
    <div className="history-card">

      <h2>Batch Analysis Activity</h2>

      <p>
        Daily BENIGN and DDoS classifications
        across saved batch analyses.
      </p>

      {/* EXPORT CSV BUTTON */}
      <div className="analytics-export">
        <button
          type="button"
          onClick={exportToCSV}
          disabled={loading || data.length === 0 || !!error}
        >
          ↓ Export CSV
        </button>
      </div>

      {/* TIME FILTERS */}
      <div className="timeline-filters">

        <button
          type="button"
          className={period === '7' ? 'selected' : ''}
          onClick={() => setPeriod('7')}
        >
          7 Days
        </button>

        <button
          type="button"
          className={period === '30' ? 'selected' : ''}
          onClick={() => setPeriod('30')}
        >
          30 Days
        </button>

        <button
          type="button"
          className={period === 'all' ? 'selected' : ''}
          onClick={() => setPeriod('all')}
        >
          All Time
        </button>

      </div>

      {/* LOADING STATE */}
      {loading && (
        <p>Loading batch activity...</p>
      )}

      {/* ERROR STATE */}
      {error && (
        <p className="detection-error">{error}</p>
      )}

      {/* EMPTY STATE */}
      {!loading && !error && data.length === 0 && (
        <p>No batch activity available.</p>
      )}

      {/* LINE CHART */}
      {!loading && !error && data.length > 0 && (
        <div className="batch-timeline-container">

          <ResponsiveContainer width="100%" height="100%">

            <LineChart data={data}>

              <CartesianGrid
                stroke="#26354b"
                strokeDasharray="3 3"
              />

              <XAxis
                dataKey="day"
                stroke="#94a3b8"
                tick={{ fontSize: 12 }}
              />

              <YAxis
                stroke="#94a3b8"
                allowDecimals={false}
              />

              {/* CUSTOM TOOLTIP */}
              <Tooltip
                content={({ active, payload, label }) => {

                  if (
                    !active ||
                    !payload ||
                    payload.length === 0
                  ) {
                    return null
                  }

                  const item = payload[0].payload

                  return (
                    <div className="custom-chart-tooltip">

                      <h4>{label}</h4>

                      <p className="tooltip-benign">
                        BENIGN: {item.benign}
                      </p>

                      <p className="tooltip-ddos">
                        DDoS: {item.ddos}
                      </p>

                      <hr />

                      <p>
                        Total Records: {item.total}
                      </p>

                      <p>
                        Batch Analyses: {item.batches}
                      </p>

                    </div>
                  )
                }}
              />

              <Legend />

              {/* BENIGN LINE */}
              <Line
                type="monotone"
                dataKey="benign"
                name="BENIGN"
                stroke="#22c55e"
                strokeWidth={3}
                dot={{ r: 5 }}
                activeDot={{ r: 8 }}
              />

              {/* DDoS LINE */}
              <Line
                type="monotone"
                dataKey="ddos"
                name="DDoS"
                stroke="#f87171"
                strokeWidth={3}
                dot={{ r: 5 }}
                activeDot={{ r: 8 }}
              />

            </LineChart>

          </ResponsiveContainer>

        </div>
      )}

    </div>
  )
}

export default BatchTimelineChart
