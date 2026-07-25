export default function Navbar({ title, onToggleSidebar }) {
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
        <div className="search-bar">
          <input type="text" placeholder="Search..." className="search-input" />
        </div>
      </div>
    </header>
  )
}
