import { Link } from "react-router-dom";

import "../../styles/layout/navbar.css";

export default function Navbar() {
  const isLoggedIn = !!localStorage.getItem("token");

  const logout = () => {
    localStorage.removeItem("token");

    window.location.href = "/login";
  };

  return (
    <header className="navbar">
      <div className="navbar-container">
        {/* =========================
            BRAND
        ========================= */}
        <Link to="/" className="navbar-logo">
          <img
            src="/favicon.png"
            alt="EnterpriseRAG AI"
            className="logo-image"
          />

          <span className="logo-title">EnterpriseRAG AI</span>
        </Link>

        {/* =========================
            NAVIGATION
        ========================= */}
        <nav className="navbar-links">
          <Link to="/features">Infrastructure</Link>

          <Link to="/docs">Docs</Link>

          <Link to="/about">Architecture</Link>
        </nav>

        {/* =========================
            ACTIONS
        ========================= */}
        <div className="navbar-actions">
          {!isLoggedIn ? (
            <>
              <Link to="/login" className="login-link">
                Sign In
              </Link>

              <Link to="/signup" className="signup-btn">
                Access Platform
              </Link>
            </>
          ) : (
            <button onClick={logout} className="logout-btn">
              Logout
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
