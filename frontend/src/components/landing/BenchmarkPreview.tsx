import "../../styles/pages/benchmark.css";

const benchmarks = [
  {
    title: "Throughput",
    value: "~850 req/sec",
    description:
      "Sustained concurrent throughput under realtime inference workloads.",
  },

  {
    title: "p95 Latency",
    value: "480ms",
    description:
      "Stable tail latency during semantic retrieval and streaming execution.",
  },

  {
    title: "Error Rate",
    value: "<1%",
    description:
      "Reliable request handling under concurrency spikes and async workloads.",
  },

  {
    title: "Tracing",
    value: "Distributed",
    description:
      "OpenTelemetry-powered observability and request lifecycle diagnostics.",
  },
];

export default function BenchmarkPreview() {
  return (
    <section className="benchmark-section">
      <div className="benchmark-container">
        {/* =========================
            HEADER
        ========================= */}
        <div className="benchmark-header">
          <span className="benchmark-badge">Infrastructure Metrics</span>

          <h2 className="benchmark-title">Performance Benchmarks</h2>

          <p className="benchmark-description">
            Observability-driven infrastructure optimized for low-latency
            semantic retrieval, realtime streaming, and scalable async request
            handling.
          </p>
        </div>

        {/* =========================
            METRICS GRID
        ========================= */}
        <div className="benchmark-grid">
          {benchmarks.map((item, index) => (
            <div key={index} className="benchmark-card">
              <span className="benchmark-card-title">{item.title}</span>

              <h3 className="benchmark-card-value">{item.value}</h3>

              <p className="benchmark-card-description">{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
