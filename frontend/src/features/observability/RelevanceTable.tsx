interface MetricEntry {
  id: string;
  timestamp: string;
  query: string;
  top_score: number;
  chunk_count: number;
  source_documents: string[];
  is_low_confidence: boolean;
}
interface Props {
  entries: MetricEntry[];
}
export default function RelevanceTable({ entries }: Props) {
  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6 overflow-x-auto">
      <h3 className="text-xl font-semibold mb-3">Top Retrieved Chunks</h3>
      {entries.length === 0 ? (
        <p className="text-neutral-400">No queries recorded yet.</p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-neutral-400 border-b border-neutral-800">
              <th className="py-2 pr-4">Query</th>
              <th className="py-2 pr-4">Score</th>
              <th className="py-2 pr-4">Chunks</th>
              <th className="py-2 pr-4">Sources</th>
              <th className="py-2">Time</th>
            </tr>
          </thead>
          <tbody>
            {entries.slice(0, 10).map((e) => (
              <tr key={e.id} className="border-b border-neutral-800/60">
                <td className="py-2 pr-4 max-w-xs truncate" title={e.query}>{e.query}</td>
                <td className="py-2 pr-4">
                  <span className={e.is_low_confidence ? "text-red-400 font-medium" : "text-emerald-400 font-medium"}>
                    {e.top_score.toFixed(3)}
                  </span>
                </td>
                <td className="py-2 pr-4 text-neutral-300">{e.chunk_count}</td>
                <td className="py-2 pr-4 text-neutral-400 max-w-[10rem] truncate">{e.source_documents.join(", ") || "-"}</td>
                <td className="py-2 text-neutral-500">{new Date(e.timestamp).toLocaleTimeString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
