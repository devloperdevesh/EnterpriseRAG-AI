export default function ChatHistory({ chats, open, onClose }: any) {
  return (
    <>
      {/* Overlay */}
      {open && (
        <div 
          className="menu-overlay"
          onClick={onClose}
        />
      )}

      {/* Drawer */}
      <div className={`side-menu ${open ? "open" : ""}`}>
        <h3>Chat History</h3>

        {!chats.length && (
          <p style={{ fontSize: 13 }}>No chats yet</p>
        )}

        {chats.map((chat: any, idx: number) => (
          <div key={idx} style={{ marginBottom: 18 }}>

            {/* Question Bubble */}
            <div style={{
              background: "var(--brand)",
              color: "white",
              padding: "10px 14px",
              borderRadius: "10px",
              fontSize: 13,
              marginLeft: "auto",
              maxWidth: "90%"
            }}>
              {chat.question}
            </div>

            {/* Answer Bubble */}
            <div style={{
              background: "#F3F4F6",
              padding: "10px 14px",
              borderRadius: "10px",
              fontSize: 13,
              marginTop: 6,
              maxWidth: "90%"
            }}>
              {chat.answer}
            </div>

          </div>
        ))}

        <button onClick={onClose}>
          Close
        </button>
      </div>
    </>
  );
}
