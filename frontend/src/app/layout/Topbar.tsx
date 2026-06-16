import "./../../styles/layout/topbar.css";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";

export default function Topbar() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <div className="topbar">
      <input placeholder="Search..." />
      <button className="btn primary" onClick={handleLogout}>
        Logout
      </button>
    </div>
  );
}
