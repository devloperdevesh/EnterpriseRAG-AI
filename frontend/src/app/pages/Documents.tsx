import { useState } from "react";
import UploadDocument from "../../documents/UploadDocument";
import ChunkVisualizer from "../../components/ChunkVisualizer";

type Tab = "upload" | "visualize";

export default function Documents() {
  const [activeTab, setActiveTab] = useState<Tab>("upload");

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: "upload", label: "Upload", icon: "📤" },
    { id: "visualize", label: "Chunk Visualizer", icon: "🔬" },
  ];

  return (
    <div className="p-6 bg-neutral-950 text-white min-h-screen">
      {/* ========================= PAGE HEADER ========================= */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Documents</h1>
        <p className="text-neutral-400 mt-2">
          Manage your enterprise knowledge base and inspect how documents are
          chunked before embedding.
        </p>
      </div>

      {/* ========================= TABS ========================= */}
      <div className="flex gap-2 mb-8 border-b border-neutral-800 pb-0">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              px-5 py-2.5 text-sm font-medium rounded-t-xl transition-all
              ${
                activeTab === tab.id
                  ? "bg-white text-black"
                  : "text-neutral-400 hover:text-white hover:bg-neutral-800"
              }
            `}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </div>

      {/* ========================= TAB CONTENT ========================= */}
      <div className="bg-white rounded-2xl p-6 text-neutral-900 min-h-[400px]">
        {activeTab === "upload" && <UploadDocument />}
        {activeTab === "visualize" && <ChunkVisualizer />}
      </div>
    </div>
  );
}
