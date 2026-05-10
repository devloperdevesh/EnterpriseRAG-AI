import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

import "../styles/pages/auth.css";

export default function Login() {
  const navigate = useNavigate();

  const { login } = useAuth();

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [error, setError] = useState("");

  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);

    setError("");

    try {
      const res = await api.post("/auth/login", {
        email,
        password,
      });

      login(res.data.access_token);

      navigate("/dashboard");
    } catch {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* =========================
            LOGO
        ========================= */}
        <img src="/favicon.png" alt="EnterpriseRAG AI" className="auth-logo" />

        {/* =========================
            TITLE
        ========================= */}
        <h1 className="auth-title">EnterpriseRAG AI</h1>

        <p className="auth-subtitle">
          Observability-driven AI infrastructure platform
        </p>

        {/* =========================
            INPUTS
        ========================= */}
        <div className="auth-form">
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          {error && <p className="auth-error">{error}</p>}

          <button onClick={submit} disabled={loading} className="auth-button">
            {loading ? "Signing In..." : "Access Platform"}
          </button>
        </div>

        {/* =========================
            FOOTER
        ========================= */}
        <p className="auth-footer">
          New to EnterpriseRAG AI?
          <Link to="/signup">Create account</Link>
        </p>
      </div>
    </div>
  );
}
