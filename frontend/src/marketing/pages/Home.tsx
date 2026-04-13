import Navbar from "../components/Navbar";

function Home() {
  return (
    <div style={{ background: "#0f172a", minHeight: "100vh", color: "white" }}>

      {/* NAVBAR */}
      <Navbar />

      {/* HERO */}
      <section
        style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          textAlign: "center",
          padding: "120px 20px",
        }}
      >
        <h1
          style={{
            fontSize: "3.5rem",
            fontWeight: 700,
            lineHeight: "1.2",
            maxWidth: "900px",
          }}
        >
          Enterprise AI for
          <span style={{ color: "#3b82f6" }}> Document Intelligence</span>
        </h1>

        <p
          style={{
            marginTop: "20px",
            fontSize: "1.2rem",
            color: "#9ca3af",
            maxWidth: "600px",
          }}
        >
          Query your documents like ChatGPT. Built on high-performance RAG architecture
          delivering sub-500ms responses at scale.
        </p>

        <div style={{ marginTop: "30px", display: "flex", gap: "15px" }}>
          <button className="btn">Start Free Trial</button>
          <button
            style={{
              padding: "10px 16px",
              borderRadius: "8px",
              background: "#1f2937",
              color: "white",
              border: "1px solid #374151",
            }}
          >
            View Demo
          </button>
        </div>

        {/* METRICS */}
        <div
          style={{
            marginTop: "40px",
            display: "flex",
            gap: "30px",
            color: "#9ca3af",
            fontSize: "0.9rem",
          }}
        >
          <span>⚡ 850+ req/sec</span>
          <span>⚡ 480ms latency</span>
          <span>⚡ Multi-tenant SaaS</span>
        </div>
      </section>

      {/* FEATURES */}
      <section style={{ padding: "80px 40px", maxWidth: "1100px", margin: "auto" }}>
        <h2 style={{ fontSize: "2rem", marginBottom: "40px" }}>
          Powerful AI Capabilities
        </h2>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: "20px" }}>
          {[
            "📄 Multi-format document support",
            "🔍 Semantic search (FAISS)",
            "⚡ Sub-second AI responses",
            "📚 Grounded answers (no hallucination)",
            "🔐 Multi-tenant secure architecture",
            "📊 Real-time performance monitoring",
          ].map((text, i) => (
            <div key={i} className="card">
              {text}
            </div>
          ))}
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section style={{ padding: "80px 40px", maxWidth: "1000px", margin: "auto" }}>
        <h2 style={{ fontSize: "2rem", marginBottom: "30px" }}>
          How It Works
        </h2>

        <div style={{ display: "flex", gap: "20px" }}>
          <div className="card">1. Upload Documents</div>
          <div className="card">2. Ask Questions</div>
          <div className="card">3. Get AI Answers</div>
        </div>
      </section>

      {/* CTA */}
      <section
        style={{
          textAlign: "center",
          padding: "100px 20px",
          borderTop: "1px solid #1f2937",
        }}
      >
        <h2 style={{ fontSize: "2rem" }}>
          Ready to build AI at scale?
        </h2>

        <button className="btn" style={{ marginTop: "20px" }}>
          Get Started
        </button>
      </section>

    </div>
  );
}

export default Home;