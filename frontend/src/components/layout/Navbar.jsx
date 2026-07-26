import { useTheme } from '../../contexts/ThemeContext'

export default function Navbar({ title, onToggleSidebar }) {
  const { theme, toggleTheme } = useTheme()
  return (
    <header className="navbar">
      <div className="navbar-left">
        <button className="hamburger" onClick={onToggleSidebar}>
          <span />
          <span />
          <span />
        </button>
        <h1 className="page-title">{title}</h1>
      </div>
      <div className="navbar-right">
        <button
          className="theme-toggle"
          type="button"
          onClick={toggleTheme}
          aria-label={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
          title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`}
        >
          <span aria-hidden="true">{theme === 'dark' ? '☀' : '☾'}</span>
          <span className="theme-label">{theme === 'dark' ? 'Light' : 'Dark'}</span>
        </button>
        <div className="search-bar">
          <input type="text" placeholder="Search..." className="search-input" />
        </div>
      </div>
    </header>
  )
}
