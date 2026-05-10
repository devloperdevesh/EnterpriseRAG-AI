import { useState } from "react";

export default function Documents() {
  const [loading] = useState(false);

  const [docs] = useState([
    "invoice.pdf",
    "report.docx",
    "architecture-spec.pdf",
    "tenant-metrics.xlsx",
  ]);

  if (loading) {
    return <div className="p-6 text-white">Loading documents...</div>;
  }

  return (
    <div
      className="
        p-6
        bg-neutral-950
        text-white
        min-h-screen
      "
    >
      {/* =========================
          PAGE HEADER
      ========================= */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Documents</h1>

        <p className="text-neutral-400 mt-2">
          Manage uploaded enterprise documents and retrieval assets.
        </p>
      </div>

      {/* =========================
          DOCUMENT LIST
      ========================= */}
      <div className="space-y-4">
        {docs.map((doc, index) => (
          <div
            key={index}
            className="
              border
              border-neutral-800
              bg-neutral-900
              rounded-2xl
              p-4
              transition-all
              hover:border-neutral-700
            "
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">{doc}</h3>

                <p className="text-sm text-neutral-500 mt-1">
                  Ready for semantic retrieval
                </p>
              </div>

              <button
                className="
                  px-4
                  py-2
                  rounded-xl
                  bg-white
                  text-black
                  text-sm
                  font-medium
                "
              >
                Open
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
