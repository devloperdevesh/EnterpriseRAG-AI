import RAGPipelineFlow from "../components/RAGPipelineFlow";
import ChunkVisualizer from "../components/ChunkVisualizer";
import ObservabilityPanel from "../components/ObservabilityPanel";
import Counter from "../hooks/Counter";

export default function Dashboard() {
  
  return (
    <div className="flex flex-col gap-6 p-6">

      {/* Top stats */}
      <div className="grid grid-cols-3 gap-6">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur">
          <p className="text-sm text-white/50 sm:text-xs">Documents</p>
          <p className="mt-1 text-3xl font-bold text-white md:text-4xl sm:text-sm"><Counter target={102348} /></p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur">
          <p className="text-sm text-white/50 sm:text-xs">Requests/sec</p>
          <p className="mt-1 text-3xl font-bold text-white md:text-4xl sm:text-sm"><Counter target={8742} /></p>
        </div>
        <div className="rounded-2xl border border-white/10 bg-white/5 p-6 text-center backdrop-blur">
          <p className="text-sm text-white/50 sm:text-xs">Latency</p>
          <p className="mt-1 text-3xl font-bold text-white md:text-4xl sm:text-sm"><Counter target={420} /></p>
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