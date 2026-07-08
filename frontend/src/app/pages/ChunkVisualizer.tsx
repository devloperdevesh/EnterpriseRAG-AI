import { useState } from "react";
import { api } from "../../api/client";

interface ChunkInfo {
  index: number;
  text: string;
  start_word: number;
  end_word: number;
  word_count: number;
  overlap_prev: number;
  overlap_next: number;
}

const CHUNK_COLORS = [
  "bg-blue-500/20 border-blue-500",
  "bg-emerald-500/20 border-emerald-500",
  "bg-amber-500/20 border-amber-500",
  "bg-violet-500/20 border-violet-500",
  "bg-rose-500/20 border-rose-500",
  "bg-cyan-500/20 border-cyan-500",
  "bg-lime-500/20 border-lime-500",
  "bg-orange-500/20 border-orange-500",
];

export default function ChunkVisualizer() {
  const [text, setText] = useState("");
  const [chunkSize, setChunkSize] = useState(300);
  const [overlap, setOverlap] = useState(30);
  const [chunks, setChunks] = useState<ChunkInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState<number | null>(null);
  const [error, setError] = useState("");

  const preview = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await api.post("/rag/chunk-preview", {
        text,
        chunk_size: chunkSize,
        overlap,
      });
      setChunks(res.data.chunks);
      setSelected(null);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to preview chunks");
      setChunks([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 bg-neutral-950 text-white min-h-screen">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Chunking Visualizer</h1>
        <p className="text-neutral-400 mt-2">
          Preview how documents are split into chunks before vector embedding.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Controls */}
        <div className="space-y-6 lg:col-span-1">
          <div className="border border-neutral-800 bg-neutral-900 rounded-2xl p-5 space-y-5">
            <div>
              <label className="block text-sm font-medium mb-1">Document text</label>
              <textarea
                className="w-full h-40 bg-neutral-950 border border-neutral-700 rounded-xl p-3 text-sm text-white resize-none outline-none focus:border-blue-500"
                placeholder="Paste or type document content here..."
                value={text}
                onChange={(e) => setText(e.target.value)}
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Chunk size: <span className="text-blue-400">{chunkSize}</span> words
              </label>
              <input
                type="range"
                min={50}
                max={1000}
                step={50}
                value={chunkSize}
                onChange={(e) => setChunkSize(Number(e.target.value))}
                className="w-full accent-blue-500"
              />
              <div className="flex justify-between text-xs text-neutral-500 mt-1">
                <span>50</span>
                <span>1000</span>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-1">
                Overlap: <span className="text-amber-400">{overlap}</span> words
              </label>
              <input
                type="range"
                min={0}
                max={Math.max(chunkSize - 1, 1)}
                step={10}
                value={overlap}
                onChange={(e) => setOverlap(Number(e.target.value))}
                className="w-full accent-amber-500"
              />
              <div className="flex justify-between text-xs text-neutral-500 mt-1">
                <span>0</span>
                <span>{chunkSize - 1}</span>
              </div>
            </div>

            <button
              onClick={preview}
              disabled={loading || !text.trim()}
              className="w-full px-4 py-3 rounded-xl bg-white text-black font-medium text-sm disabled:opacity-40 hover:bg-neutral-200 transition-colors"
            >
              {loading ? "Chunking..." : "Preview Chunks"}
            </button>
          </div>

          {error && (
            <div className="border border-red-800 bg-red-900/20 rounded-2xl p-4 text-sm text-red-400">
              {error}
            </div>
          )}

          {chunks.length > 0 && (
            <div className="border border-neutral-800 bg-neutral-900 rounded-2xl p-5 text-sm space-y-2">
              <h3 className="font-medium text-neutral-300">Summary</h3>
              <p>Total chunks: <span className="text-white">{chunks.length}</span></p>
              <p>
                Total words:{" "}
                <span className="text-white">
                  {chunks.reduce((s, c) => s + c.word_count, 0)}
                </span>
              </p>
              <p>
                Avg words/chunk:{" "}
                <span className="text-white">
                  {Math.round(
                    chunks.reduce((s, c) => s + c.word_count, 0) / chunks.length
                  )}
                </span>
              </p>
            </div>
          )}
        </div>

        {/* Chunk visualization */}
        <div className="lg:col-span-2">
          {chunks.length === 0 && !loading && (
            <div className="border border-neutral-800 bg-neutral-900 rounded-2xl p-12 text-center text-neutral-500">
              Paste text and click Preview Chunks to see the breakdown.
            </div>
          )}

          {loading && (
            <div className="border border-neutral-800 bg-neutral-900 rounded-2xl p-12 text-center text-neutral-500">
              Chunking...
            </div>
          )}

          {chunks.length > 0 && !loading && (
            <div className="space-y-3">
              {chunks.map((chunk) => {
                const colorIdx = chunk.index % CHUNK_COLORS.length;
                const isSelected = selected === chunk.index;

                return (
                  <div
                    key={chunk.index}
                    onClick={() =>
                      setSelected(selected === chunk.index ? null : chunk.index)
                    }
                    className={`
                      border rounded-2xl p-4 cursor-pointer transition-all
                      ${CHUNK_COLORS[colorIdx]}
                      ${isSelected ? "ring-2 ring-white/30 scale-[1.01]" : "opacity-80 hover:opacity-100"}
                    `}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs font-mono uppercase tracking-wider text-white/60">
                        Chunk #{chunk.index + 1}
                      </span>
                      <span className="text-xs font-mono text-white/40">
                        {chunk.word_count} words
                      </span>
                    </div>

                    <p className="text-sm leading-relaxed line-clamp-3">
                      {chunk.text}
                    </p>

                    {isSelected && (
                      <div className="mt-3 pt-3 border-t border-white/10 text-xs font-mono text-white/60 space-y-1">
                        <p>Start word: {chunk.start_word}</p>
                        <p>End word: {chunk.end_word}</p>
                        <p>Overlap from previous: {chunk.overlap_prev} words</p>
                        <p>Overlap to next: {chunk.overlap_next} words</p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
