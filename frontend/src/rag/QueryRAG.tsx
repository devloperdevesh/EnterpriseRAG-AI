import { useRef, useState } from "react";
import "../styles/pages/chat.css";
import { streamQuery } from "../services/chatService";
import QueryHistoryPanel from "./QueryHistoryPanel";

interface ChatMessage {
  type: "user" | "ai";
  text: string;
  lens?: string;
}

export default function QueryRAG() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [query, setQuery] = useState("");
  const [lens, setLens] = useState("summary");
  const [loading, setLoading] = useState(false);
  // Bumped after each query so the history panel refetches.
  const [historyRefresh, setHistoryRefresh] = useState(0);
  // Synchronous in-flight guard: `loading` state only updates on the next
  // render, so a fast double-Enter/click could otherwise fire twice.
  const inFlight = useRef(false);

  const handleAsk = async () => {
    if (!query.trim() || inFlight.current) return;
    inFlight.current = true;

    const question = query.trim();
    setQuery("");
    setMessages((prev) => [
      ...prev,
      { type: "user", text: question },
      { type: "ai", text: "Thinking...", lens },
    ]);
    setLoading(true);

    try {
      let streamed = "";
      await streamQuery(question, {
        onToken: (chunk) => {
          streamed += chunk;
          setMessages((prev) => [
            ...prev.slice(0, -1),
            { type: "ai", text: streamed, lens },
          ]);
        },
      });
      // A new entry was just recorded server-side -- refresh the panel.
      setHistoryRefresh((n) => n + 1);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Something went wrong.";
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { type: "ai", text: `⚠️ ${message}`, lens },
      ]);
    } finally {
      inFlight.current = false;
      setLoading(false);
    }
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

            {msg.type === "ai" && msg.lens && (
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
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Ask your document..."
          disabled={loading}
        />

        <button
          onClick={handleAsk}
          className="btn primary"
          disabled={loading}
        >
          {loading ? "..." : "Send"}
        </button>
      </div>

      {/* 🕘 QUERY HISTORY */}
      <QueryHistoryPanel refreshKey={historyRefresh} />

    </div>
  );
}
