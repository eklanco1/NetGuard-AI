
import { useCallback, useEffect, useState } from 'react'
import './SecurityAlerts.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function SecurityAlerts() {
  const [alerts, setAlerts] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('All')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [resolvingId, setResolvingId] = useState(null)

  const loadAlerts = useCallback(async () => {
    try {
      const [alertsResponse, statsResponse] = await Promise.all([
        fetch(`${API_URL}/api/v1/alerts?status=${filter}&limit=100`),
        fetch(`${API_URL}/api/v1/alerts/stats`)
      ])

      if (!alertsResponse.ok || !statsResponse.ok) {
        throw new Error('Failed to load security alerts')
      }

      const alertsData = await alertsResponse.json()
      const statsData = await statsResponse.json()

      setAlerts(alertsData.alerts || [])
      setStats(statsData)
      setError('')
    } catch (err) {
      setError(err.message || 'Unable to load alerts')
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => {
    setLoading(true)
    loadAlerts()

    const timer = setInterval(loadAlerts, 5000)
    return () => clearInterval(timer)
  }, [loadAlerts])

  async function resolveAlert(id) {
    setResolvingId(id)

    try {
      const response = await fetch(
        `${API_URL}/api/v1/alerts/${id}/resolve`,
        { method: 'PATCH' }
      )

      if (!response.ok) {
        throw new Error('Failed to resolve alert')
      }

      await loadAlerts()
    } catch (err) {
      setError(err.message || 'Unable to resolve alert')
    } finally {
      setResolvingId(null)
    }
  }

  function formatDate(date) {
    if (!date) return '-'
    return new Date(date).toLocaleString()
  }

  return (
    <div className="alerts-page">
      <div className="alerts-header">
        <div>
          <h1>Security Alerts</h1>
          <p>Review and manage simulated network security alerts</p>
        </div>

        <button
          className="alerts-refresh"
          onClick={loadAlerts}
        >
          ↻ Refresh
        </button>
      </div>

      <div className="alerts-stats">
        <div className="alerts-stat">
          <span>Total Alerts</span>
          <strong>{stats?.total ?? 0}</strong>
          <small>All recorded alerts</small>
        </div>

        <div className="alerts-stat">
          <span>Active Alerts</span>
          <strong className="alerts-red">
            {stats?.active ?? 0}
          </strong>
          <small>Require review</small>
        </div>

        <div className="alerts-stat">
          <span>Resolved Alerts</span>
          <strong className="alerts-green">
            {stats?.resolved ?? 0}
          </strong>
          <small>Marked as resolved</small>
        </div>

        <div className="alerts-stat">
          <span>Critical Active</span>
          <strong className="alerts-orange">
            {stats?.critical ?? 0}
          </strong>
          <small>Critical severity</small>
        </div>
      </div>

      <div className="alerts-panel">
        <div className="alerts-panel-header">
          <div>
            <h2>Alert History</h2>
            <p>Automatically generated DDoS simulation alerts</p>
          </div>

          <select
            value={filter}
            onChange={e => setFilter(e.target.value)}
            aria-label="Filter alerts by status"
          >
            <option value="All">All Alerts</option>
            <option value="Active">Active</option>
            <option value="Resolved">Resolved</option>
          </select>
        </div>

        {error && (
          <div className="alerts-error" role="alert">
            {error}
          </div>
        )}

        {loading ? (
          <div className="alerts-empty">Loading alerts...</div>
        ) : (
          <div className="alerts-table-wrap">
            <table className="alerts-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Threat</th>
                  <th>Severity</th>
                  <th>Probability</th>
                  <th>Source</th>
                  <th>Status</th>
                  <th>Created At</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {alerts.map(alert => (
                  <tr key={alert.id}>
                    <td>#{alert.id}</td>
                    <td>
                      <strong>{alert.alert_type}</strong>
                      <small className="alerts-description">
                        {alert.description}
                      </small>
                    </td>
                    <td>
                      <span className={`alerts-severity ${alert.severity.toLowerCase()}`}>
                        {alert.severity}
                      </span>
                    </td>
                    <td>
                      {alert.ddos_probability_percent == null
                        ? '-'
                        : `${Number(alert.ddos_probability_percent).toFixed(2)}%`}
                    </td>
                    <td>{alert.source}</td>
                    <td>
                      <span className={`alerts-status ${alert.status.toLowerCase()}`}>
                        {alert.status}
                      </span>
                    </td>
                    <td>{formatDate(alert.created_at)}</td>
                    <td>
                      {alert.status === 'Active' ? (
                        <button
                          className="alerts-resolve"
                          disabled={resolvingId === alert.id}
                          onClick={() => resolveAlert(alert.id)}
                        >
                          {resolvingId === alert.id
                            ? 'Saving...'
                            : 'Resolve'}
                        </button>
                      ) : (
                        <span className="alerts-resolved-label">
                          Resolved
                        </span>
                      )}
                    </td>
                  </tr>
                ))}

                {alerts.length === 0 && (
                  <tr>
                    <td colSpan="8" className="alerts-empty">
                      No alerts found.
                      Start Network Monitoring to generate simulated alerts.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default SecurityAlerts