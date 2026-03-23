import { api } from "../api/client";

export const sendQuery = (query: string) => {
  return api.post("/rag/query", { query });
};