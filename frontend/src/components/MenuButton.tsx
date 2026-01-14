export default function MenuButton({ onClick }: { onClick: () => void }) {
    return (
      <button className="nav-btn" onClick={onClick}>
        ☰ Menu
      </button>
    );
  }
  