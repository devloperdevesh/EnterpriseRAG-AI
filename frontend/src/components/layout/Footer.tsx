

export default function Footer() {
  return (
    <footer className="footer">
      {/* =========================
          MAIN FOOTER
      ========================= */}
      <div className="footer-container">
        {/* =========================
            LEFT BRAND
        ========================= */}
        <div className="footer-brand">
          <div className="footer-logo-row">
            <img
              src="/favicon.png"
              alt="EnterpriseRAG AI"
              className="footer-logo"
            />

            <div className="footer-brand-content">
              <h2 className="footer-brand-title">EnterpriseRAG AI</h2>

              <p className="footer-brand-description">
                Distributed AI infrastructure platform engineered for
                observability-first inference systems, semantic retrieval,
                realtime streaming, and scalable async orchestration.
              </p>
            </div>
          </div>
        </div>

        {/* =========================
            RIGHT GRID
        ========================= */}
        <div className="footer-grid">
          {/* PLATFORM */}
          <div className="footer-column">
            <h4>Platform</h4>

            <a href="/features">Infrastructure</a>

            <a href="/about">Architecture</a>

            <a href="/docs">Documentation</a>

            <a href="/dashboard">Dashboard</a>
          </div>

          {/* TECHNOLOGY */}
          <div className="footer-column">
            <h4>Technology</h4>

            <span>FastAPI</span>

            <span>Redis</span>

            <span>Docker</span>

            <span>OpenTelemetry</span>
          </div>

          {/* OBSERVABILITY */}
          <div className="footer-column">
            <h4>Observability</h4>

            <span>Grafana</span>

            <span>Jaeger</span>

            <span>Prometheus</span>

            <span>Distributed Tracing</span>
          </div>
        </div>
      </div>

      {/* =========================
          FOOTER BOTTOM
      ========================= */}
      <div className="footer-bottom">
        <p>© 2026 EnterpriseRAG AI</p>

        <p>Distributed Systems • Observability • AI Infrastructure</p>
      </div>
    </footer>
  );
}
