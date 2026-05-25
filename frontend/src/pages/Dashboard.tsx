import RAGPipelineFlow from "../components/RAGPipelineFlow";
import ChunkVisualizer from "../components/ChunkVisualizer";
import ObservabilityPanel from "../components/ObservabilityPanel";

export default function Dashboard() {
  return (
    <div className="flex flex-col gap-6 p-6">

      {/* Top stats */}
      <div className="grid grid-cols-3 gap-6">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur">
          <p className="text-sm text-white/50">Documents</p>
          <p className="mt-1 text-3xl font-bold text-white">102,348</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur">
          <p className="text-sm text-white/50">Requests/sec</p>
          <p className="mt-1 text-3xl font-bold text-white">8,742</p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur">
          <p className="text-sm text-white/50">Latency</p>
          <p className="mt-1 text-3xl font-bold text-white">~420ms</p>
        </div>
      </div>

      {/* RAG Pipeline Flow */}
      <RAGPipelineFlow />

      {/* Chunk Visualizer */}
      <ChunkVisualizer />

      {/* Observability Panel */}
      <ObservabilityPanel />

    </div>
  );
}