import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="w-64 bg-black p-5">

      <h2 className="mb-6 font-bold text-xl">
        EnterpriseRAG
      </h2>

      <nav className="flex flex-col gap-3">
        <Link to="/dashboard">Dashboard</Link>
        <Link to="/chat">Chat</Link>
        <Link to="/documents">Documents</Link>
        <Link to="/analytics">Analytics</Link>
        <Link to="/billing">Billing</Link>
        <Link to="/settings">Settings</Link>
      </nav>

    </div>
  );
}