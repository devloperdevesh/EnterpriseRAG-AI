interface MetricEntry {
  timestamp: string;
  retrieval_latency_ms: number;
  llm_latency_ms: number;
  total_latency_ms: number;
}
interface Props {
  entries: MetricEntry[];
}
export default function LatencyChart({ entries }: Props) {
  const recent = entries.slice(0, 20).reverse();
  const max = Math.max(1, ...recent.map((e) => e.total_latency_ms));
  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
      <h3 className="text-xl font-semibold mb-3">Latency Chart</h3>
      {recent.length === 0 ? (
        <p className="text-neutral-400">No queries recorded yet.</p>
      ) : (
        <svg viewBox="0 0 400 120" className="w-full h-32">
          <polyline
            fill="none"
            stroke="#818cf8"
            strokeWidth="2"
            points={recent.map((e, i) => {
              const x = (i / Math.max(1, recent.length - 1)) * 400;
              const y = 120 - (e.total_latency_ms / max) * 110 - 5;
              return `${x},${y}`;
            }).join(" ")}
          />
        </svg>
      )}
      <p className="text-neutral-500 text-sm mt-3">Last {recent.length} queries - total latency (ms)</p>
    </div>
  );
}
