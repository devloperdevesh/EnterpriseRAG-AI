import "./../../styles/layout/topbar.css";
import ThemeToggle from "../../components/ThemeToggle";
export default function Topbar() {
  return (
    <div className="topbar flex items-center justify-between">
      <input placeholder="Search..." />
      <div className="flex items-center gap-4">
        <ThemeToggle />
        <button className="btn primary">New</button>
      </div>
    </div>
  );
}