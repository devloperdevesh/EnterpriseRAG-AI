import { useState } from "react";
import ChatHistory from "./ChatHistory";

export default function QueryRAG() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [chats, setChats] = useState<any[]>([]);
  const [openHistory, setOpenHistory] = useState(false);

  const ask = async () => {
    if (!question.trim()) return;

    setAnswer("");
    setLoading(true);

    const res = await fetch("http://127.0.0.1:8000/rag/query/stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`
      },
      body: JSON.stringify({ question })
    });

    const reader = res.body?.getReader();
    const decoder = new TextDecoder();
    let finalAnswer = "";

    if (!reader) return;

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value);
      finalAnswer += chunk;
      setAnswer(prev => prev + chunk);
    }

    setChats(prev => [...prev, { question, answer: finalAnswer }]);
    setQuestion("");
    setLoading(false);
  };

  return (
    <>
      {/* Chat History Button */}
      <button 
        className="nav-btn" 
        style={{ marginBottom: 12 }}
        onClick={() => setOpenHistory(true)}
      >
        Chat History
      </button>

      {/* Main Ask Card */}
      <div className="card">
        <h3>Ask Knowledge Base</h3>
        <p>Ask questions and get AI-powered answers from your documents</p>

        <input
          className="textbox"
          placeholder="Ask a question..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <button 
          className="primary" 
          style={{ marginTop: 14, width: "100%" }}
          onClick={ask}
        >
          {loading ? "Thinking..." : "Ask AI"}
        </button>

        {answer && (
          <div className="card" style={{ marginTop: 15 }}>
            {answer}
          </div>
        )}
      </div>

      {/* Slide-in History Drawer */}
      <ChatHistory 
        chats={chats}
        open={openHistory}
        onClose={() => setOpenHistory(false)}
      />
    </>
  );
}
