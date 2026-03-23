import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div className="flex justify-between p-4 bg-black text-white">

      <h1>EnterpriseRAG AI</h1>

      <div className="flex gap-6">
        <Link to="/">Home</Link>
        <Link to="/features">Features</Link>
        <Link to="/pricing">Pricing</Link>
        <Link to="/how-it-works">How it Works</Link>
        <Link to="/docs">Docs</Link>
        <Link to="/api-docs">API</Link>
      </div>

      <div className="flex gap-4">
        <Link to="/login">Login</Link>
        <Link to="/signup">Signup</Link>
      </div>

    </div>
  );
}
const logout = () => {
  localStorage.removeItem("token");
  window.location.href = "/login";
};

<button onClick={logout}>Logout</button>

import { Link } from "react-router-dom";

export default function Navbar() {
  return (
    <div className="flex justify-between p-4 border-b">

      <h1 className="font-bold text-xl">
        🚀 EnterpriseRAG
      </h1>

      <div className="flex gap-4">
        <Link to="/">Home</Link>
        <Link to="/features">Features</Link>
        <Link to="/pricing">Pricing</Link>
      </div>

    </div>
  );
}