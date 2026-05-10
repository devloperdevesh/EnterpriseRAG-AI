import "../../styles/pages/cta.css";

export default function CTA() {
  return (
    <section className="cta-section">
      <div className="cta-container">
        {/* =========================
            BADGE
        ========================= */}
        <span className="cta-badge">Production AI Infrastructure</span>

        {/* =========================
            TITLE
        ========================= */}
        <h2 className="cta-title">
          Built for scalable distributed AI systems.
        </h2>

        {/* =========================
            DESCRIPTION
        ========================= */}
        <p className="cta-description">
          Observability-first backend infrastructure engineered for semantic
          retrieval, realtime streaming, distributed tracing, and
          high-concurrency inference workloads.
        </p>

        {/* =========================
            ACTIONS
        ========================= */}
        <div className="cta-actions">
          <a href="/docs" className="primary-cta-btn">
            Explore API Docs
          </a>

          <a href="/about" className="secondary-cta-btn">
            View Architecture
          </a>
        </div>

        {/* =========================
            METRICS
        ========================= */}
        <div className="cta-metrics">
          <div className="cta-metric">
            <span className="cta-metric-value">~850 req/sec</span>

            <span className="cta-metric-label">Throughput</span>
          </div>

          <div className="cta-metric">
            <span className="cta-metric-value">480ms p95</span>

            <span className="cta-metric-label">Latency</span>
          </div>

          <div className="cta-metric">
            <span className="cta-metric-value">&lt;1%</span>

            <span className="cta-metric-label">Error Rate</span>
          </div>
        </div>
      </div>
    </section>
  );
}
