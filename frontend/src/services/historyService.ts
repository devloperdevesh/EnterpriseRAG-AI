import { api } from "../api/client";

/** A single recorded RAG query with its latency and retrieval metadata. */
export interface QueryHistoryEntry {
  id: string;
  query: string;
  answer_summary: string;
  chunk_count: number;
  top_scores: number[];
  source_documents: string[];
  retrieval_latency_ms: number;
  llm_latency_ms: number;
  total_latency_ms: number;
  timestamp: string;
}

export interface QueryHistoryResponse {
  scope: string;
  count: number;
  items: QueryHistoryEntry[];
}

/** Fetch the current user's most recent queries from `GET /rag/history`. */
export async function getQueryHistory(
  limit = 20,
): Promise<QueryHistoryResponse> {
  const { data } = await api.get<QueryHistoryResponse>("/rag/history", {
    params: { limit },
  });
  return data;
}
