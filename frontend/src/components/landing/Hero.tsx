import "../../styles/pages/home.css";

export default function Hero() {
  return (
    <section className="hero-section">
      <div className="hero-container">
        {/* =========================
            BRAND BADGE
        ========================= */}
        <div className="hero-badge">Production-Grade AI Infrastructure</div>

        {/* =========================
            HEADLINE
        ========================= */}
        <h1 className="hero-title">
          Observability-Driven
          <br />
          Retrieval Infrastructure
        </h1>

        {/* =========================
            SUBTITLE
        ========================= */}
        <p className="hero-description">
          Distributed Retrieval-Augmented Generation infrastructure engineered
          for low-latency semantic retrieval, realtime streaming, and traceable
          AI inference workflows.
        </p>

        {/* =========================
            ACTIONS
        ========================= */}
        <div className="hero-actions">
          <button className="primary-btn">View Architecture</button>

          <button className="secondary-btn">Explore API</button>
        </div>

        {/* =========================
            METRICS
        ========================= */}
        <div className="hero-metrics">
          <div className="metric-card">
            <span className="metric-value">~850 req/sec</span>

            <span className="metric-label">Sustained Throughput</span>
          </div>

          <div className="metric-card">
            <span className="metric-value">480ms p95</span>

            <span className="metric-label">Latency</span>
          </div>

          <div className="metric-card">
            <span className="metric-value">&lt;1%</span>

            <span className="metric-label">Error Rate</span>
          </div>
        </div>
      </div>
    </section>
  );
}
