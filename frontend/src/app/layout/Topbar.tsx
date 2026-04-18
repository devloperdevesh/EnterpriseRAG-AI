import "./../../styles/layout/topbar.css";

export default function Topbar() {
  return (
    <div className="topbar">
      <input placeholder="Search..." />
      <button className="btn primary">New</button>
    </div>
  );
}