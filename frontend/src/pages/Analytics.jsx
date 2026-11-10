
import TrafficDistribution from '../components/TrafficDistribution'
import BatchStatsCards from '../components/BatchStatsCards'
import BatchComparisonChart from '../components/BatchComparisonChart'
import BatchTimelineChart from '../components/BatchTimelineChart'

function Analytics() {
  return (
    <div className="analytics-page">

      <div className="analytics-header">
        <h1>Security Analytics</h1>

        <p>
          Detailed insights into network traffic
          and AI-based threat detection.
        </p>
      </div>

      <TrafficDistribution />

      <BatchStatsCards />

      <div className="analytics-charts-grid">
        <BatchComparisonChart />
        <BatchTimelineChart />
      </div>

    </div>
  )
}

export default Analytics
