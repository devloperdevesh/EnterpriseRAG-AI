import { type FormEvent, useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";

import "../styles/pages/auth.css";

export default function Login() {
  const navigate = useNavigate();

  const location = useLocation();

  const { isAuthenticated, login } = useAuth();

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [error, setError] = useState("");

  const [loading, setLoading] = useState(false);

  const redirectTo =
    new URLSearchParams(location.search).get("next") ||
    (location.state as { from?: { pathname?: string } } | null)?.from
      ?.pathname ||
    "/dashboard";

  useEffect(() => {
    if (isAuthenticated) {
      navigate(redirectTo, { replace: true });
    }
  }, [isAuthenticated, navigate, redirectTo]);

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setLoading(true);

    setError("");

    try {
      const res = await api.post("/auth/login", {
        email,
        password,
      });

      login(res.data.access_token);

      navigate(redirectTo, { replace: true });
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
        <form className="auth-form" onSubmit={submit}>
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" disabled={loading} className="auth-button">
            {loading ? "Signing In..." : "Access Platform"}
          </button>
        </form>

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
