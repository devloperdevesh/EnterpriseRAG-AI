import { useState } from "react";

export default function ThemeToggle() {
  const [dark, setDark] = useState(true);

  return (
    <button
      onClick={() => setDark(!dark)}
      className="theme-toggle-btn"
    >
      {dark ? "Dark" : "Light"}
    </button>
  );
}
