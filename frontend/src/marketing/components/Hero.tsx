export default function Hero() {
    return (
      <div className="text-center py-24">
  
        <h1 className="text-6xl font-bold">
          AI-Powered Document Intelligence
        </h1>
  
        <p className="mt-4 text-gray-400">
          Process 100K+ documents with sub-second AI retrieval
        </p>
  
        <div className="mt-6 flex justify-center gap-4">
          <button className="bg-blue-500 px-6 py-2 rounded">
            Start Free Trial
          </button>
  
          <button className="border px-6 py-2 rounded">
            View Demo
          </button>
        </div>
  
      </div>
    );
  }

  import { useState } from "react";

export default function StreamingChat() {
  const [text, setText] = useState("");

  const fakeStream = async () => {
    let res = "AI response streaming...";
    let out = "";

    for (let c of res) {
      await new Promise((r) => setTimeout(r, 20));
      out += c;
      setText(out);
    }
  };

  return (
    <div>
      <button onClick={fakeStream}>Ask</button>
      <p>{text}</p>
    </div>
  );
}