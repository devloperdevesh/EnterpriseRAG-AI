import { useState } from "react";
import UploadDocument from "../documents/UploadDocument";
import QueryRAG from "../rag/QueryRAG";
import MenuButton from "../components/MenuButton";
import SideMenu from "../components/SideMenu";

export default function Dashboard() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <>
      {/* Top Navbar */}
      <div className="topbar">
        <div className="brand">
          EnterpriseRAG <span>AI</span>
        </div>

        <MenuButton onClick={() => setMenuOpen(true)} />
      </div>

      {/* Side Menu */}
      <SideMenu open={menuOpen} onClose={() => setMenuOpen(false)} />

      {/* Main Content */}
      <div className="content">
        <UploadDocument />
        <QueryRAG />
      </div>
    </>
  );
}
