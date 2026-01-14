type Props = {
    children: React.ReactNode;
    onClick?: () => void;
    type?: "button" | "submit";
  };
  
  export default function Button({ children, onClick, type = "button" }: Props) {
    return (
      <button
        type={type}
        onClick={onClick}
        style={{
          width: "100%",
          padding: "14px",
          borderRadius: 12,
          border: "none",
          fontWeight: 600,
          color: "white",
          cursor: "pointer",
          background: "linear-gradient(90deg,#6366F1,#0EA5E9)",
          boxShadow: "0 10px 25px rgba(99,102,241,0.35)",
        }}
      >
        {children}
      </button>
    );
  }
  