import ThemeToggle from "../../components/ThemeToggle";

export default function Settings() {
  return (
    <div className="settings-page">
      {/* ================= HEADER ================= */}
      <div className="settings-header">
        <h1>Platform Settings</h1>

        <p>
          Manage appearance, infrastructure preferences, and platform
          configuration.
        </p>
      </div>

      {/* ================= SETTINGS GRID ================= */}
      <div className="settings-grid">
        {/* APPEARANCE */}
        <div className="settings-card">
          <div className="settings-card-header">
            <h2>Appearance</h2>
            <span>UI Preferences</span>
          </div>

          <div className="settings-item">
            <div>
              <h3>Dark Mode</h3>
              <p>Toggle dashboard appearance theme</p>
            </div>

            <ThemeToggle />
          </div>
        </div>

        {/* PLATFORM */}
        <div className="settings-card">
          <div className="settings-card-header">
            <h2>Platform</h2>
            <span>Infrastructure Configuration</span>
          </div>

          <div className="settings-item">
            <div>
              <h3>Observability</h3>
              <p>Metrics, tracing, and runtime monitoring enabled</p>
            </div>

            <span className="status enabled">Active</span>
          </div>

          <div className="settings-item">
            <div>
              <h3>Failure Replay System</h3>
              <p>Automatic failed request replay workflows</p>
            </div>

            <span className="status enabled">Enabled</span>
          </div>
        </div>

        {/* PERFORMANCE */}
        <div className="settings-card">
          <div className="settings-card-header">
            <h2>Performance</h2>
            <span>Runtime Optimization</span>
          </div>

          <div className="settings-item">
            <div>
              <h3>Cache Optimization</h3>
              <p>Redis-backed low-latency optimization</p>
            </div>

            <span className="status healthy">Healthy</span>
          </div>

          <div className="settings-item">
            <div>
              <h3>LLM Routing</h3>
              <p>Multi-provider orchestration system</p>
            </div>

            <span className="status healthy">Operational</span>
          </div>
        </div>
      </div>
    </div>
  );
}
