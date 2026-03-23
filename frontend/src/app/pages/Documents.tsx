import { useState } from "react";

export default function Documents() {
  const [docs] = useState([
    "invoice.pdf",
    "report.docx",
  ]);

  return (
    <div className="glass p-6">

      <h2 className="mb-4">Documents</h2>

      {docs.map((d, i) => (
        <div key={i} className="border p-2 mb-2">
          {d}
        </div>
      ))}

    </div>
  );
}