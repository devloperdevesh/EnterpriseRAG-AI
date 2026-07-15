import "./../../styles/layout/topbar.css";
import { useNavigate } from "react-router-dom";

import ThemeToggle from "../../components/ThemeToggle";
import { useAuth } from "../../context/AuthContext";

export default function Topbar() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="topbar flex items-center justify-between">
      <input placeholder="Search..." />
      <div className="flex items-center gap-4">
        <ThemeToggle />
        <button className="btn primary" onClick={handleLogout}>
          Logout
        </button>
      </div>
    </div>
  );
}
