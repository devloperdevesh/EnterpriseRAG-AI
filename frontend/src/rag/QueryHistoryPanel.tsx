import { useCallback, useEffect, useState } from "react";
import {
  getQueryHistory,
  type QueryHistoryEntry,
} from "../services/historyService";
import "../styles/pages/query-history.css";

/** Human-readable relative time, e.g. "just now", "3m ago", "2h ago". */
function timeAgo(iso: string): string {
  const seconds = Math.round((Date.now() - new Date(iso).getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  return `${Math.round(minutes / 60)}h ago`;
}

interface QueryHistoryPanelProps {
  /** Bump this value to trigger a refresh (e.g. after a new query). */
  refreshKey?: number;
}

/**
 * Collapsible panel that lists the current user's recent RAG queries with
 * per-query latency and retrieval metadata. Backed by `GET /rag/history`.
 */
export default function QueryHistoryPanel({
  refreshKey = 0,
}: QueryHistoryPanelProps) {
  const [open, setOpen] = useState(true);
  const [entries, setEntries] = useState<QueryHistoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getQueryHistory(20);
      setEntries(data.items);
    } catch {
      setError("Could not load query history.");
    } finally {
      setLoading(false);
    }
  }, []);

  // Load on mount and whenever the parent signals a refresh.
  useEffect(() => {
    loadHistory();
  }, [loadHistory, refreshKey]);

  return (
    <div className="qh-panel">
      <div className="qh-header">
        <button
          className="qh-toggle"
          onClick={() => setOpen((v) => !v)}
          aria-expanded={open}
        >
          <span
            className={`qh-chevron ${open ? "open" : ""}`}
            aria-hidden="true"
          >
            ▸
          </span>
          Query History ({entries.length})
        </button>
        <button
          className="qh-refresh"
          onClick={loadHistory}
          disabled={loading}
          title="Refresh history"
          aria-label="Refresh history"
        >
          {loading ? "…" : "⟳"}
        </button>
      </div>

      {open && (
        <div className="qh-body">
          {/* ENHANCEMENT: MORE HELPFUL ERROR STATE WITH RETRY */}
          {error && (
            <div className="qh-empty error-fallback-state">
              <p> {error}</p>
              <button 
                className="btn primary qh-retry-btn" 
                onClick={loadHistory}
                disabled={loading}
                style={{ 
                  marginTop: "12px", 
                  padding: "6px 14px", 
                  fontSize: "13px",
                  backgroundColor: "#000000",
                  color: "#ffffff",
                  border: "none",
                  borderRadius: "6px",
                  cursor: "pointer",
                  fontWeight: "500"
                }}
              >
                {loading ? "Reconnecting..." : "Retry Connection"}
              </button>
            </div>
          )}

          {/* ENHANCEMENT: VISUAL LOADING SKELETON */}
          {loading && !error && entries.length === 0 && (
            <div className="qh-skeleton-container" style={{ opacity: 0.6, padding: "8px" }}>
              <p className="qh-empty">Verifying connection pipeline...</p>
              {[1, 2, 3].map((i) => (
                <div key={i} style={{ height: "34px", background: "rgba(0,0,0,0.05)", borderRadius: "4px", margin: "6px 0" }} />
              ))}
            </div>
          )}
          {!error && !loading && entries.length === 0 && (
            <p className="qh-empty">No queries yet.</p>
          )}

          {entries.map((entry) => {
            const expanded = expandedId === entry.id;
            return (
              <div key={entry.id} className="qh-entry">
                <button
                  className="qh-entry-head"
                  onClick={() => setExpandedId(expanded ? null : entry.id)}
                  aria-expanded={expanded}
                >
                  <span
                    className={`qh-chevron ${expanded ? "open" : ""}`}
                    aria-hidden="true"
                  >
                    ▸
                  </span>
                  <span className="qh-query" title={entry.query}>
                    {entry.query}
                  </span>
                </button>

                <div className="qh-meta">
                  <span className="qh-badge">
                    ⏱ {Math.round(entry.total_latency_ms)}ms
                  </span>
                  <span className="qh-badge">
                    📦 {entry.chunk_count} chunks
                  </span>
                  <span className="qh-time">🕑 {timeAgo(entry.timestamp)}</span>
                </div>

                {expanded && (
                  <div className="qh-detail">
                    <div className="qh-detail-row">
                      <span className="qh-label">Latency</span>
                      <span>
                        retrieval {Math.round(entry.retrieval_latency_ms)}ms
                        {" · "}
                        LLM {Math.round(entry.llm_latency_ms)}ms
                      </span>
                    </div>
                    <div className="qh-detail-row">
                      <span className="qh-label">Top scores</span>
                      <span>
                        {entry.top_scores.length
                          ? entry.top_scores
                              .map((s) => s.toFixed(2))
                              .join(" · ")
                          : "—"}
                      </span>
                    </div>
                    <div className="qh-detail-row">
                      <span className="qh-label">Sources</span>
                      <span className="qh-sources">
                        {entry.source_documents.length ? (
                          entry.source_documents.map((doc) => (
                            <span key={doc} className="qh-chip">
                              {doc}
                            </span>
                          ))
                        ) : (
                          <span>—</span>
                        )}
                      </span>
                    </div>
                    {entry.answer_summary && (
                      <div className="qh-detail-row">
                        <span className="qh-label">Answer</span>
                        <span className="qh-answer">
                          {entry.answer_summary}
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
