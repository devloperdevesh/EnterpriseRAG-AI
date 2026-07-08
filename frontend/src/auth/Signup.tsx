import { useState } from "react";

import { Link } from "react-router-dom";

import { api } from "../api/client";

import "../styles/pages/auth.css";

export default function Signup() {
  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [tenantId, setTenantId] = useState("");

  const [message, setMessage] = useState("");

  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!email || !password || !tenantId) {
      setMessage("All fields are required");

      return;
    }

    console.log(password.length);
    setLoading(true);

    setMessage("");

    try {
      const res = await api.post("/auth/signup", {
        email,
        password,
        tenant_id: tenantId.trim(),
        role: "user",
      });

      setMessage(res.data.message || "Account created successfully");
    } catch (err: any) {
      const msg =
        err.response?.data?.detail?.[0]?.msg ||
        err.response?.data?.detail ||
        "Signup failed";

      setMessage(String(msg));
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
        <h1 className="auth-title">Create Workspace</h1>

        <p className="auth-subtitle">
          Provision tenant-scoped infrastructure access
        </p>

        {/* =========================
            FORM
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

          <input
            type="text"
            placeholder="Workspace ID"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
          />

          {message && <p className="auth-message">{message}</p>}

          <button onClick={submit} disabled={loading} className="auth-button">
            {loading ? "Provisioning..." : "Create Account"}
          </button>
        </div>

        {/* =========================
            FOOTER
        ========================= */}
        <p className="auth-footer">
          Already have access?
          <Link to="/login">Sign in</Link>
        </p>
      </div>
    </div>
  );
}
