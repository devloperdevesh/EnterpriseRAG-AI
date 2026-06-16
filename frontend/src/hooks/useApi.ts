import { useState } from "react";

export function useApi(fn: any) {
  const [loading, setLoading] = useState(false);

  const call = async (...args: any) => {
    setLoading(true);
    try {
      const res = await fn(...args);
      return res;
    } finally {
      setLoading(false);
    }
  };

  return { call, loading };
}