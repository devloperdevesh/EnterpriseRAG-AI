import Sidebar from "./Sidebar";
import { Outlet } from "react-router-dom";

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-[#020617] text-white">

      <Sidebar />

      <div className="flex-1 p-6 overflow-y-auto">
        <Outlet />
      </div>

    </div>
  );
}