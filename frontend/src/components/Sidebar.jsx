
import { NavLink } from 'react-router'

function Sidebar() {
  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <span className="logo-icon">◆</span>
        <h2>NetGuard AI</h2>
      </div>

      <p className="sidebar-label">MAIN MENU</p>

      <nav className="sidebar-nav">

        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            isActive ? 'nav-item active' : 'nav-item'
          }
        >
          Dashboard
        </NavLink>

        <NavLink
          to="/detection"
          className={({ isActive }) =>
            isActive ? 'nav-item active' : 'nav-item'
          }
        >
          AI Detection
        </NavLink>

        <NavLink
          to="/history"
          className={({ isActive }) =>
            isActive ? 'nav-item active' : 'nav-item'
          }
        >
          Prediction History
        </NavLink>

        <NavLink
          to="/analytics"
          className={({ isActive }) =>
            isActive ? 'nav-item active' : 'nav-item'
          }
        >
          Analytics
        </NavLink>

        <NavLink
          to="/ai-assistant"
          className={({ isActive }) =>
            isActive ? 'nav-item active' : 'nav-item'
          }
        >
          AI Assistant
        </NavLink>
      
      </nav>

      <div className="sidebar-footer">
        <span className="status-dot"></span>
        <span>System Online</span>
      </div>

    </aside>
  )
}

export default Sidebar
