import { useState } from "react";

export function useApi(fn: any) {
  const [loading, setLoading] = useState(false);

  const call = async (...args: any) => {
    setLoading(true);
    const res = await fn(...args);
    setLoading(false);
    return res;
  };

  return { call, loading };
}