
import { useEffect, useRef, useState } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

import './Monitoring.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
const MAX_POINTS = 30

function Monitoring() {
  const [running, setRunning] = useState(false)
  const [intervalSeconds, setIntervalSeconds] = useState(3)
  const [traffic, setTraffic] = useState([])
  const [error, setError] = useState('')
  const [lastResult, setLastResult] = useState(null)

  const counterRef = useRef(0)
  const busyRef = useRef(false)

  const total = traffic.length
  const ddosCount = traffic.filter(p => p.prediction === 'DDoS').length
  const benignCount = total - ddosCount

  useEffect(() => {
    if (!running) return

    let cancelled = false

    async function fetchSample() {
      if (busyRef.current) return
      busyRef.current = true

      try {
        // Simulacija: oko 30% zahtjeva koristi DDoS uzorak
        const scenario = Math.random() < 0.3 ? 'DDoS' : 'BENIGN'

        const response = await fetch(
          `${API_URL}/api/v1/monitoring/sample?scenario=${encodeURIComponent(scenario)}`
        )

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }

        const result = await response.json()

        if (cancelled) return

        // Automatsko kreiranje upozorenja za DDoS
        // Samo za rezultate simuliranog monitoringa.
        if (result.prediction === 'DDoS') {
          try {
            const alertResponse = await fetch(
              `${API_URL}/api/v1/alerts`,
              {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                  prediction: result.prediction,
                  ddos_probability_percent:
                    result.ddos_probability_percent,
                  source: 'simulation'
                })
              }
            )

            if (!alertResponse.ok) {
              throw new Error('Alert could not be saved')
            }
          } catch (alertError) {
            console.error('Security Alert error:', alertError)
            if (!cancelled) {
              setError(
                'Traffic analyzed, but the security alert could not be saved.'
              )
            }
          }
        }

        if (cancelled) return
        counterRef.current += 1

        const point = {
          ...result,
          id: counterRef.current,
          time: new Date().toLocaleTimeString(),
          benign: result.prediction === 'BENIGN' ? 1 : 0,
          ddos: result.prediction === 'DDoS' ? 1 : 0
        }

        setTraffic(prev => [...prev, point].slice(-MAX_POINTS))
        setLastResult(point)
        setError('')
      } catch (err) {
        if (!cancelled) {
          setError(err.message || 'Monitoring request failed')
          setRunning(false)
        }
      } finally {
        busyRef.current = false
      }
    }

    fetchSample()
    const timer = setInterval(fetchSample, intervalSeconds * 1000)

    return () => {
      cancelled = true
      clearInterval(timer)
    }
  }, [running, intervalSeconds])

  function resetMonitoring() {
    setRunning(false)
    setTraffic([])
    setLastResult(null)
    setError('')
    counterRef.current = 0
  }

  return (
    <div className="monitoring-page">
      <div className="monitoring-header">
        <div>
          <h1>Network Traffic Monitoring</h1>
          <p>AI-powered simulated network traffic analysis</p>
        </div>

        <span className="monitoring-mode">
          DEMO SIMULATION
        </span>
      </div>

      <div className="monitoring-controls">
        <div className="monitoring-state">
          <span className={`monitoring-dot ${running ? 'running' : ''}`} />
          {running ? 'Simulation Running' : 'Simulation Paused'}
        </div>

        <div className="monitoring-actions">
          <select
            value={intervalSeconds}
            onChange={e => setIntervalSeconds(Number(e.target.value))}
            aria-label="Simulation interval"
          >
            <option value={2}>Every 2 seconds</option>
            <option value={3}>Every 3 seconds</option>
            <option value={5}>Every 5 seconds</option>
          </select>

          <button
            className="monitoring-primary"
            onClick={() => setRunning(prev => !prev)}
          >
            {running ? 'Pause Simulation' : 'Start Simulation'}
          </button>

          <button
            className="monitoring-secondary"
            onClick={resetMonitoring}
          >
            Reset
          </button>
        </div>
      </div>

      {error && (
        <div className="monitoring-error" role="alert">
          {error}
        </div>
      )}

      <div className="monitoring-stats">
        <div className="monitoring-stat">
          <span>Total Analyzed</span>
          <strong>{total}</strong>
          <small>Current session (last {MAX_POINTS})</small>
        </div>

        <div className="monitoring-stat">
          <span>Benign Traffic</span>
          <strong className="monitoring-green">{benignCount}</strong>
          <small>Classified as BENIGN</small>
        </div>

        <div className="monitoring-stat">
          <span>DDoS Detected</span>
          <strong className="monitoring-red">{ddosCount}</strong>
          <small>Classified as DDoS</small>
        </div>

        <div className="monitoring-stat">
          <span>Latest Classification</span>
          <strong className={lastResult?.prediction === 'DDoS' ? 'monitoring-red' : 'monitoring-green'}>
            {lastResult?.prediction || 'Waiting'}
          </strong>
          <small>
            {lastResult
              ? `${lastResult.ddos_probability_percent}% DDoS probability`
              : 'No samples analyzed'}
          </small>
        </div>
      </div>

      {lastResult?.prediction === 'DDoS' && (
        <div className="monitoring-alert" role="status">
          <strong>âš  DDoS Activity Detected</strong>
          <p>
            The latest simulated traffic sample was classified as DDoS.
            Estimated DDoS probability: {lastResult.ddos_probability_percent}%.
          </p>
        </div>
      )}

      <div className="monitoring-panel">
        <h2>Traffic Classification Timeline</h2>
        <p>Classification of the last {MAX_POINTS} simulated traffic samples</p>

        <div className="monitoring-chart">
          {traffic.length === 0 ? (
            <div className="monitoring-empty">
              Start the simulation to visualize network traffic.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={traffic}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253449" />
                <XAxis dataKey="id" stroke="#94a3b8" />
                <YAxis
                  stroke="#94a3b8"
                  domain={[0, 1]}
                  ticks={[0, 1]}
                  allowDecimals={false}
                />
                <Tooltip
                  contentStyle={{
                    background: '#172338',
                    border: '1px solid #334155',
                    color: '#fff'
                  }}
                  formatter={(value, name) => [
                    value ? 'Detected' : 'Not detected',
                    name
                  ]}
                />
                <Line
                  type="stepAfter"
                  dataKey="benign"
                  name="BENIGN"
                  stroke="#22c55e"
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
                <Line
                  type="stepAfter"
                  dataKey="ddos"
                  name="DDoS"
                  stroke="#ef4444"
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={false}
                />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="monitoring-panel">
        <h2>Recent Traffic Activity</h2>
        <p>Latest simulated samples processed by the ML model</p>

        <div className="monitoring-table-wrap">
          <table className="monitoring-table">
            <thead>
              <tr>
                <th>Time</th>
                <th>Input Sample</th>
                <th>Prediction</th>
                <th>DDoS Probability</th>
                <th>Packets / sec</th>
              </tr>
            </thead>
            <tbody>
              {[...traffic].reverse().slice(0, 10).map(item => (
                <tr key={item.id}>
                  <td>{item.time}</td>
                  <td>{item.sample_type}</td>
                  <td>
                    <span className={`monitoring-class ${item.prediction === 'DDoS' ? 'ddos' : 'benign'}`}>
                      {item.prediction}
                    </span>
                  </td>
                  <td>{item.ddos_probability_percent}%</td>
                  <td>{item.packets_per_second}</td>
                </tr>
              ))}
              {traffic.length === 0 && (
                <tr>
                  <td colSpan="5" className="monitoring-empty-row">
                    No monitoring activity yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Monitoring
