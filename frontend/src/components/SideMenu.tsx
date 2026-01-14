import { useAuth } from "../context/AuthContext";

export default function SideMenu({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { logout } = useAuth();

  return (
    <>
      {open && <div className="menu-overlay" onClick={onClose}></div>}

      <div className={`side-menu ${open ? "open" : ""}`}>
        <h3>EnterpriseRAG</h3>

        <button className="nav-btn" onClick={() => alert("Chat History coming soon 🚀")}>
          💬 Chat History
        </button>

        <button className="nav-btn" onClick={() => alert("My Documents coming soon 📄")}>
          📂 My Documents
        </button>

        <button className="nav-btn" onClick={logout}>
          🚪 Logout
        </button>
      </div>
    </>
  );
}
