import { API_BASE_URL } from "../api/client";

export interface StreamQueryOptions {
  /** Called with each chunk of text as the backend streams the answer. */
  onToken?: (chunk: string) => void;
}

/**
 * Send a question to the RAG streaming endpoint.
 *
 * The backend streams the answer as `text/plain`; chunks are surfaced
 * incrementally via `onToken`, and the full answer is returned when complete.
 */
export async function streamQuery(
  question: string,
  { onToken }: StreamQueryOptions = {},
): Promise<string> {
  const token = localStorage.getItem("token");

  const response = await fetch(`${API_BASE_URL}/rag/query/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ question }),
  });

  if (!response.ok) {
    throw new Error(`Query failed (${response.status})`);
  }

  // Fallback for environments without a readable stream body.
  if (!response.body) {
    const text = await response.text();
    onToken?.(text);
    return text.trim();
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let answer = "";
  let done = false;

  while (!done) {
    const result = await reader.read();
    done = result.done;
    if (result.value) {
      const chunk = decoder.decode(result.value, { stream: true });
      answer += chunk;
      onToken?.(chunk);
    }
  }

  // Flush the decoder: emits any trailing multi-byte character that was
  // split across the final chunk boundary.
  const tail = decoder.decode();
  if (tail) {
    answer += tail;
    onToken?.(tail);
  }

  return answer.trim();
}
