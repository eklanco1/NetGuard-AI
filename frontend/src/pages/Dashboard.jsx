
import { useEffect, useState } from 'react'

import StatsCards from '../components/StatsCards'
import ThreatChart from '../components/ThreatChart'
import PredictionTable from '../components/PredictionTable'

function Dashboard() {

  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {

    async function fetchStats() {
      try {
        const response = await fetch(
          'http://127.0.0.1:8000/api/v1/predictions/stats'
        )

        if (!response.ok) {
          throw new Error('Failed to fetch statistics')
        }

        const data = await response.json()
        setStats(data)

      } catch (err) {
        console.error(err)
        setError('Unable to load statistics.')

      } finally {
        setLoading(false)
      }
    }

    fetchStats()

  }, [])

  return (
    <>
      <h1>Security Dashboard</h1>

      <p>
        Monitor network traffic and AI detection results.
      </p>

      {loading && <p>Loading statistics...</p>}

      {error && <p>{error}</p>}

      {stats && <StatsCards stats={stats} />}

      <ThreatChart />

      <PredictionTable />
    </>
  )
}

export default Dashboard
