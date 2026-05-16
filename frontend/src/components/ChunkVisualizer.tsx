import { useState } from "react";
import { motion } from "framer-motion";

const sampleChunks = [
  {
    id: 1,
    text: "EnterpriseRAG AI is a production-oriented distributed RAG platform engineered for high-concurrency AI workloads.",
    tokens: 18,
    similarity: 0.92,
    color: "#6366f1",
  },
  {
    id: 2,
    text: "The system combines asynchronous API execution, distributed tracing, realtime streaming and semantic retrieval.",
    tokens: 16,
    similarity: 0.87,
    color: "#8b5cf6",
  },
  {
    id: 3,
    text: "FAISS vector store enables sub-millisecond similarity search across millions of embedded document chunks.",
    tokens: 15,
    similarity: 0.78,
    color: "#a855f7",
  },
  {
    id: 4,
    text: "Redis queue isolation ensures async workload separation and prevents blocking under sustained concurrent load.",
    tokens: 14,
    similarity: 0.65,
    color: "#d946ef",
  },
  {
    id: 5,
    text: "OpenTelemetry distributed tracing provides full request lifecycle visibility across all infrastructure layers.",
    tokens: 13,
    similarity: 0.54,
    color: "#ec4899",
  },
];

export default function ChunkVisualizer() {
  const [selected, setSelected] = useState<number | null>(null);

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">
          Document Chunk Visualizer
        </h2>
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-white/60">
          {sampleChunks.length} chunks
        </span>
      </div>

      <div className="flex flex-col gap-3">
        {sampleChunks.map((chunk) => (
          <motion.div
            key={chunk.id}
            onClick={() => setSelected(selected === chunk.id ? null : chunk.id)}
            whileHover={{ scale: 1.01 }}
            className="cursor-pointer rounded-xl border border-white/10 bg-white/5 p-4"
            style={{
              borderLeftColor: chunk.color,
              borderLeftWidth: 4,
            }}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-white/60">
                Chunk #{chunk.id}
              </span>
              <div className="flex gap-3">
                <span className="text-xs text-white/50">
                  🪙 {chunk.tokens} tokens
                </span>
                <span className="text-xs text-white/50">
                  🎯 {(chunk.similarity * 100).toFixed(0)}% match
                </span>
              </div>
            </div>

            <p className="mt-2 text-sm text-white/80">{chunk.text}</p>

            {selected === chunk.id && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="mt-3 rounded-lg bg-white/5 p-3"
              >
                <div className="mb-1 text-xs text-white/40">
                  Similarity Score
                </div>
                <div className="h-2 w-full rounded-full bg-white/10">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${chunk.similarity * 100}%` }}
                    transition={{ duration: 0.6 }}
                    className="h-2 rounded-full"
                    style={{ backgroundColor: chunk.color }}
                  />
                </div>
                <div className="mt-1 text-right text-xs text-white/40">
                  {(chunk.similarity * 100).toFixed(1)}%
                </div>
              </motion.div>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}