
function StatsCards({ stats }) {

  const cards = [
    {
      title: "Total Predictions",
      value: stats.total_predictions,
      color: "blue"
    },
    {
      title: "BENIGN Traffic",
      value: stats.benign_predictions,
      color: "green"
    },
    {
      title: "DDoS Detected",
      value: stats.ddos_predictions,
      color: "red"
    },
    {
      title: "DDoS Percentage",
      value: `${stats.ddos_percentage}%`,
      color: "purple"
    }
  ]

  return (
    <div className="stats-grid">
      {cards.map((card) => (
        <div
          className={`stat-card ${card.color}`}
          key={card.title}
        >
          <p>{card.title}</p>
          <h2>{card.value}</h2>
        </div>
      ))}
    </div>
  )
}

export default StatsCards
