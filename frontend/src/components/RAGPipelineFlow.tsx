import { useState } from "react";
import { motion } from "framer-motion";

const stages = [
  { id: 1, label: "User Query", latency: "0ms", color: "#6366f1", icon: "🔍" },
  { id: 2, label: "Embedding", latency: "45ms", color: "#8b5cf6", icon: "🧠" },
  { id: 3, label: "FAISS Retrieval", latency: "120ms", color: "#a855f7", icon: "🗄️" },
  { id: 4, label: "LLM Inference", latency: "280ms", color: "#d946ef", icon: "⚡" },
  { id: 5, label: "Streaming Response", latency: "480ms", color: "#ec4899", icon: "📡" },
];

export default function RAGPipelineFlow() {
  const [active, setActive] = useState<number | null>(null);
  const [running, setRunning] = useState(false);

  const simulate = async () => {
    setRunning(true);
    setActive(null);
    for (let i = 0; i < stages.length; i++) {
      setActive(stages[i].id);
      await new Promise((r) => setTimeout(r, 600));
    }
    setRunning(false);
  };

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">RAG Pipeline Flow</h2>
        <button
          onClick={simulate}
          disabled={running}
          className="rounded-lg bg-indigo-600 px-4 py-1.5 text-sm text-white hover:bg-indigo-500 disabled:opacity-50"
        >
          {running ? "Running..." : "▶ Simulate"}
        </button>
      </div>

      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {stages.map((stage, idx) => (
          <div key={stage.id} className="flex items-center gap-2">
            <motion.div
              animate={{
                scale: active === stage.id ? 1.1 : 1,
                boxShadow:
                  active === stage.id
                    ? `0 0 20px ${stage.color}`
                    : "0 0 0px transparent",
              }}
              transition={{ duration: 0.3 }}
              className="flex min-w-[110px] flex-col items-center rounded-xl border border-white/10 bg-white/10 p-3 text-center"
            >
              <span className="text-2xl">{stage.icon}</span>
              <span className="mt-1 text-xs font-medium text-white">
                {stage.label}
              </span>
              <span className="mt-1 text-xs text-white/50">{stage.latency}</span>
              {active === stage.id && (
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 0.5 }}
                  className="mt-2 h-1 rounded-full"
                  style={{ backgroundColor: stage.color }}
                />
              )}
            </motion.div>
            {idx < stages.length - 1 && (
              <motion.span
                animate={{ opacity: active && active > stage.id ? 1 : 0.2 }}
                className="text-xl text-white"
              >
                →
              </motion.span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}