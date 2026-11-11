
import { Routes, Route } from 'react-router'

import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import Detection from './pages/Detection'
import Analytics from './pages/Analytics'
import AIAssistant from './pages/AIAssistant'
import Monitoring from './pages/Monitoring'

import SecurityAlerts from './pages/SecurityAlerts'

import './App.css'

function App() {
  return (
    <div className="app-layout">
      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/detection" element={<Detection />} />
          <Route path="/history" element={<History />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/monitoring" element={<Monitoring />} />
          <Route path="/ai-assistant" element={<AIAssistant />} />

          <Route path="/alerts" element={<SecurityAlerts />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
