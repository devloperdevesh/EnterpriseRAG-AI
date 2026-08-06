import { useEffect, useState } from "react";

interface MetricEntry {
  timestamp: string;
  total_tokens: number;
}

interface Props {
  entries: MetricEntry[];
}

export default function TokenUsageChart({ entries }: Props) {
  const recent = entries.slice(0, 20).reverse();
  const max = Math.max(1, ...recent.map((e) => e.total_tokens));

  return (
    <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-6">
      <h3 className="text-xl font-semibold mb-3">Token Usage</h3>
      {recent.length === 0 ? (
        <p className="text-neutral-400">No queries recorded yet.</p>
      ) : (
        <div className="flex items-end gap-1 h-40">
          {recent.map((e, i) => (
            <div
              key={i}
              className="flex-1 bg-emerald-500/70 hover:bg-emerald-400 rounded-t transition-colors"
              style={{ height: `${(e.total_tokens / max) * 100}%` }}
              title={`${e.total_tokens} tokens - ${new Date(e.timestamp).toLocaleTimeString()}`}
            />
          ))}
        </div>
      )}
      <p className="text-neutral-500 text-sm mt-3">
        Last {recent.length} queries - tokens per request
      </p>
    </div>
  );
}
