
import { Routes, Route } from 'react-router'

import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import Detection from './pages/Detection'
import Analytics from './pages/Analytics'
import AIAssistant from './pages/AIAssistant'
import './App.css'

function App() {
  return (
    <div className="app-layout">

      <Sidebar />

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/history" element={<History />} />
          <Route path="/detection" element={<Detection />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/ai-assistant" element={<AIAssistant />} />
        </Routes>

      </main>

    </div>
  )
}

export default App
