import { useEffect, useState } from "react";
import LatencyChart from "../features/observability/LatencyChart";
import TokenUsageChart from "../features/observability/TokenUsageChart";
import RelevanceTable from "../features/observability/RelevanceTable";
import ConfidenceAlert from "../features/observability/ConfidenceAlert";

interface MetricsResponse {
  tenant_id: string;
  count: number;
  total: number;
  summary: {
    count: number;
    avg_latency_ms: number;
    avg_retrieval_latency_ms: number;
    avg_llm_latency_ms: number;
    total_tokens: number;
    avg_tokens_per_query: number;
    low_confidence_count: number;
  };
  entries: any[];
}

const POLL_INTERVAL_MS = 30000;

export default function ObservabilityDashboard() {
  const [data, setData] = useState<MetricsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const token = localStorage.getItem("access_token");
        const res = await fetch("/api/metrics?limit=50", {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json: MetricsResponse = await res.json();
        if (!cancelled) {
          setData(json);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError((err as Error).message);
      }
    }
    load();
    const id = setInterval(load, POLL_INTERVAL_MS);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, []);

  return (
    <div className="p-8 max-w-6xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">RAG Pipeline Observability</h1>
        <p className="text-neutral-400 text-sm mt-1">Updates every 30 seconds - tenant: {data?.tenant_id ?? "-"}</p>
      </div>
      {error && (
        <div className="bg-red-950/40 border border-red-800 rounded-xl p-4 text-red-300 text-sm">
          Failed to load metrics: {error}
        </div>
      )}
      <ConfidenceAlert
        lowConfidenceCount={data?.summary.low_confidence_count ?? 0}
        totalCount={data?.summary.count ?? 0}
      />
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <LatencyChart entries={data?.entries ?? []} />
        <TokenUsageChart entries={data?.entries ?? []} />
      </div>
      <RelevanceTable entries={data?.entries ?? []} />
    </div>
  );
}
