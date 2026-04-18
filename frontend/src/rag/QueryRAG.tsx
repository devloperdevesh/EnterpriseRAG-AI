import { useState } from "react";
import "../../styles/pages/chat.css";


export default function QueryRAG() {
  const [messages, setMessages] = useState<any[]>([]);
  const [query, setQuery] = useState("");
  const [lens, setLens] = useState("summary");

  const handleAsk = async () => {
    if (!query.trim()) return;

    const newMessages = [
      ...messages,
      { type: "user", text: query },
      { type: "ai", text: "Thinking...", lens },
    ];

    setMessages(newMessages);
    setQuery("");

    // 🔥 backend connect later
    setTimeout(() => {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          type: "ai",
          text: `AI ${lens} response for your query.`,
          lens,
        },
      ]);
    }, 1000);
  };

  return (
    <div className="chat-container">

      {/* 🔥 MULTI LENS */}
      <div className="lens">
        {["summary", "risk", "insights"].map((item) => (
          <button
            key={item}
            className={lens === item ? "active" : ""}
            onClick={() => setLens(item)}
          >
            {item}
          </button>
        ))}
      </div>

      {/* 💬 CHAT */}
      <div className="chat-box">
        {messages.map((msg, i) => (
          <div key={i} className={`chat-bubble ${msg.type}`}>
            
            {msg.type === "ai" && (
              <span className="lens-tag">{msg.lens}</span>
            )}

            {msg.text}
          </div>
        ))}
      </div>

      {/* ✍️ INPUT */}
      <div className="chat-input">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Askk your document..."
        />

        <button onClick={handleAsk} className="btn primary">
          Send
        </button>
      </div>

    </div>
  );
}