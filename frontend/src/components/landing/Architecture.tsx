import "../../styles/pages/architecture.css";

export default function Architecture() {
  return (
    <section className="architecture-section">
      <div className="architecture-container">
        {/* =========================
            HEADER
        ========================= */}
        <div className="architecture-header">
          <span className="architecture-badge">Distributed Architecture</span>

          <h2 className="architecture-title">
            Observability-Driven AI Infrastructure
          </h2>

          <p className="architecture-description">
            Async-first request execution pipeline engineered for semantic
            retrieval, distributed tracing, realtime streaming, and scalable
            inference workflows.
          </p>
        </div>

        {/* =========================
            FLOW
        ========================= */}
        <div className="architecture-flow">
          <div className="flow-card">Client</div>

          <div className="flow-arrow">→</div>

          <div className="flow-card">FastAPI</div>

          <div className="flow-arrow">→</div>

          <div className="flow-card">Redis Queue</div>

          <div className="flow-arrow">→</div>

          <div className="flow-card">FAISS</div>

          <div className="flow-arrow">→</div>

          <div className="flow-card">LLM</div>

          <div className="flow-arrow">→</div>

          <div className="flow-card">Jaeger</div>
        </div>
      </div>
    </section>
  );
}
