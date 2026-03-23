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