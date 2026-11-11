import API_URL from '../config/api'

import { useEffect, useState } from 'react'

function BatchStatsCards() {

  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const controller = new AbortController()

    async function fetchBatchStats() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/predictions/batches/stats`,
          { signal: controller.signal }
        )

        if (!response.ok) {
          throw new Error('Failed to load batch statistics')
        }

        const data = await response.json()
        setStats(data)

      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error(err)
          setError('Unable to load batch statistics.')
        }

      } finally {
        if (!controller.signal.aborted) {
          setLoading(false)
        }
      }
    }

    fetchBatchStats()

    return () => controller.abort()
  }, [])

  if (loading) {
    return <p>Loading batch statistics...</p>
  }

  if (error) {
    return <p className="detection-error">{error}</p>
  }

  if (!stats) {
    return null
  }

  const cards = [
    {
      title: 'Total Batch Analyses',
      value: stats.total_batches,
      color: 'blue'
    },
    {
      title: 'Total Analyzed Records',
      value: stats.total_records,
      color: 'purple'
    },
    {
      title: 'BENIGN Records',
      value: stats.benign_records,
      color: 'green'
    },
    {
      title: 'DDoS Records',
      value: stats.ddos_records,
      color: 'red'
    }
  ]

  return (
    <section className="batch-overview">

      <h2>Batch Analysis Overview</h2>

      <p>
        Statistics from previously analyzed CSV datasets.
      </p>

      <div className="stats-grid">
        {cards.map((card) => (
          <div
            key={card.title}
            className={`stat-card ${card.color}`}
          >
            <p>{card.title}</p>
            <h2>{card.value.toLocaleString('en-US')}</h2>
          </div>
        ))}
      </div>

    </section>
  )
}

export default BatchStatsCards
