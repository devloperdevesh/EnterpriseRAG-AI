import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="sidebar">

      <h2 className="logo">EnterpriseRAG</h2>

      <nav className="nav">
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/chat">Chat</NavLink>
        <NavLink to="/documents">Documents</NavLink>
        <NavLink to="/analytics">Analytics</NavLink>
        <NavLink to="/billing">Billing</NavLink>
        <NavLink to="/settings">Settings</NavLink>
      </nav>

    </div>
  );
}