import QueryRAG from "../../rag/QueryRAG";
import "../../styles/pages/chat.css";

export default function Chat() {
  return (
    <div className="chat-page">
      <h2>AI Chat</h2>

      <QueryRAG />
    </div>
  );
}