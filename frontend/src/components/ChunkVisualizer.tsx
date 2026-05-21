import { useState, useRef } from "react";
import { api } from "../api/client";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ChunkMeta {
  index: number;
  preview: string;
  full_text: string;
  word_count: number;
  char_count: number;
  start_word: number;
  end_word: number;
}

interface PreviewResponse {
  total_words: number;
  total_chunks: number;
  chunk_size: number;
  overlap: number;
  chunks: ChunkMeta[];
}

// ---------------------------------------------------------------------------
// Colour palette — cycles through chunks for visual distinction
// ---------------------------------------------------------------------------

const CHUNK_COLORS = [
  "bg-blue-100 border-blue-300 text-blue-900",
  "bg-violet-100 border-violet-300 text-violet-900",
  "bg-emerald-100 border-emerald-300 text-emerald-900",
  "bg-amber-100 border-amber-300 text-amber-900",
  "bg-rose-100 border-rose-300 text-rose-900",
  "bg-cyan-100 border-cyan-300 text-cyan-900",
];

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ChunkVisualizer() {
  const [file, setFile] = useState<File | null>(null);
  const [chunkSize, setChunkSize] = useState(500);
  const [overlap, setOverlap] = useState(50);
  const [result, setResult] = useState<PreviewResponse | null>(null);
  const [selected, setSelected] = useState<ChunkMeta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handlePreview = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setSelected(null);

    try {
      const form = new FormData();
      form.append("file", file);
      form.append(
        "params",
        JSON.stringify({ chunk_size: chunkSize, overlap })
      );

      // Send params as query string, file as multipart body
      const res = await api.post<PreviewResponse>(
        `/documents/preview-chunks?chunk_size=${chunkSize}&overlap=${overlap}`,
        form,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      setResult(res.data);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ?? "Failed to preview chunks. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* ------------------------------------------------------------------ */}
      {/* Header                                                              */}
      {/* ------------------------------------------------------------------ */}
      <div>
        <h2 className="text-2xl font-bold text-neutral-900">
          Document Chunk Visualizer
        </h2>
        <p className="text-neutral-500 mt-1 text-sm">
          Upload a PDF to preview how it will be split before vector embedding.
          Adjust chunk size and overlap to optimise retrieval quality.
        </p>
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Controls                                                            */}
      {/* ------------------------------------------------------------------ */}
      <div className="card flex flex-col gap-5">
        {/* File picker */}
        <div>
          <label className="block text-sm font-medium text-neutral-700 mb-2">
            PDF Document
          </label>
          <div
            className="border-2 border-dashed border-neutral-300 rounded-xl p-6 text-center cursor-pointer hover:border-blue-400 transition-colors"
            onClick={() => fileRef.current?.click()}
          >
            <input
              ref={fileRef}
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            {file ? (
              <p className="text-sm font-medium text-blue-600">{file.name}</p>
            ) : (
              <p className="text-sm text-neutral-400">
                Click to select a PDF file
              </p>
            )}
          </div>
        </div>

        {/* Sliders */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Chunk Size —{" "}
              <span className="text-blue-600 font-semibold">{chunkSize} words</span>
            </label>
            <input
              type="range"
              min={50}
              max={2000}
              step={50}
              value={chunkSize}
              onChange={(e) => setChunkSize(Number(e.target.value))}
              className="w-full accent-blue-600"
            />
            <div className="flex justify-between text-xs text-neutral-400 mt-1">
              <span>50</span>
              <span>2000</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-700 mb-1">
              Overlap —{" "}
              <span className="text-violet-600 font-semibold">{overlap} words</span>
            </label>
            <input
              type="range"
              min={0}
              max={Math.min(500, chunkSize - 1)}
              step={10}
              value={overlap}
              onChange={(e) => setOverlap(Number(e.target.value))}
              className="w-full accent-violet-600"
            />
            <div className="flex justify-between text-xs text-neutral-400 mt-1">
              <span>0</span>
              <span>{Math.min(500, chunkSize - 1)}</span>
            </div>
          </div>
        </div>

        <button
          onClick={handlePreview}
          disabled={!file || loading}
          className="primary-btn self-start disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Analysing…" : "Preview Chunks"}
        </button>

        {error && (
          <p className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-4 py-3">
            {error}
          </p>
        )}
      </div>

      {/* ------------------------------------------------------------------ */}
      {/* Stats bar                                                           */}
      {/* ------------------------------------------------------------------ */}
      {result && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Total Words", value: result.total_words.toLocaleString() },
            { label: "Total Chunks", value: result.total_chunks },
            { label: "Chunk Size", value: `${result.chunk_size} words` },
            { label: "Overlap", value: `${result.overlap} words` },
          ].map((stat) => (
            <div
              key={stat.label}
              className="card text-center py-4"
            >
              <p className="text-2xl font-bold text-neutral-900">{stat.value}</p>
              <p className="text-xs text-neutral-500 mt-1">{stat.label}</p>
            </div>
          ))}
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* Chunk grid                                                          */}
      {/* ------------------------------------------------------------------ */}
      {result && (
        <div>
          <h3 className="text-lg font-semibold text-neutral-800 mb-3">
            Chunk Breakdown
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {result.chunks.map((chunk) => {
              const colorClass =
                CHUNK_COLORS[chunk.index % CHUNK_COLORS.length];
              const isSelected = selected?.index === chunk.index;

              return (
                <button
                  key={chunk.index}
                  onClick={() =>
                    setSelected(isSelected ? null : chunk)
                  }
                  className={`
                    border rounded-xl p-4 text-left transition-all
                    ${colorClass}
                    ${isSelected ? "ring-2 ring-offset-2 ring-blue-500 shadow-md" : "hover:shadow-sm"}
                  `}
                >
                  {/* Chunk header */}
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase tracking-wide opacity-70">
                      Chunk {chunk.index + 1}
                    </span>
                    <span className="text-xs opacity-60">
                      {chunk.word_count}w · {chunk.char_count}c
                    </span>
                  </div>

                  {/* Preview text */}
                  <p className="text-sm leading-relaxed line-clamp-4">
                    {chunk.preview}
                  </p>

                  {/* Word range */}
                  <p className="text-xs opacity-50 mt-2">
                    Words {chunk.start_word}–{chunk.end_word}
                  </p>
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ------------------------------------------------------------------ */}
      {/* Detail drawer                                                       */}
      {/* ------------------------------------------------------------------ */}
      {selected && (
        <div className="card border-blue-200 bg-blue-50">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold text-blue-900">
              Chunk {selected.index + 1} — Full Text
            </h4>
            <button
              onClick={() => setSelected(null)}
              className="text-blue-400 hover:text-blue-700 text-lg leading-none"
              aria-label="Close"
            >
              ✕
            </button>
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4 text-center">
            <div className="bg-white rounded-lg py-2">
              <p className="text-lg font-bold text-blue-700">{selected.word_count}</p>
              <p className="text-xs text-neutral-500">Words</p>
            </div>
            <div className="bg-white rounded-lg py-2">
              <p className="text-lg font-bold text-blue-700">{selected.char_count}</p>
              <p className="text-xs text-neutral-500">Characters</p>
            </div>
            <div className="bg-white rounded-lg py-2">
              <p className="text-lg font-bold text-blue-700">
                {selected.start_word}–{selected.end_word}
              </p>
              <p className="text-xs text-neutral-500">Word Range</p>
            </div>
          </div>

          <pre className="text-sm text-blue-900 whitespace-pre-wrap leading-relaxed bg-white rounded-lg p-4 max-h-64 overflow-y-auto">
            {selected.full_text}
          </pre>
        </div>
      )}
    </div>
  );
}
