import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const metrics = [
  { label: "Requests/sec", value: "850", icon: "⚡", color: "#6366f1" },
  { label: "P95 Latency", value: "480ms", icon: "⏱️", color: "#8b5cf6" },
  { label: "Error Rate", value: "<1%", icon: "🛡️", color: "#a855f7" },
  { label: "Queue Depth", value: "12", icon: "📊", color: "#d946ef" },
];

const generatePoint = (prev: number) =>
  Math.max(200, Math.min(900, prev + (Math.random() - 0.5) * 100));

const initialData = Array.from({ length: 10 }, (_, i) => ({
  time: `${i}s`,
  rps: Math.floor(Math.random() * 400 + 600),
  latency: Math.floor(Math.random() * 200 + 350),
}));

export default function ObservabilityPanel() {
  const [data, setData] = useState(initialData);

  useEffect(() => {
    const interval = setInterval(() => {
      setData((prev) => {
        const last = prev[prev.length - 1];
        const next = {
          time: `${prev.length}s`,
          rps: Math.floor(generatePoint(last.rps)),
          latency: Math.floor(generatePoint(last.latency)),
        };
        return [...prev.slice(-19), next];
      });
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur">
      <h2 className="mb-4 text-lg font-semibold text-white">
        Observability Dashboard
      </h2>

      {/* Metric Cards */}
      <div className="mb-6 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {metrics.map((m) => (
          <div
            key={m.label}
            className="rounded-xl border border-white/10 bg-white/5 p-4 text-center"
          >
            <div className="text-2xl">{m.icon}</div>
            <div
              className="mt-1 text-xl font-bold"
              style={{ color: m.color }}
            >
              {m.value}
            </div>
            <div className="mt-1 text-xs text-white/50">{m.label}</div>
          </div>
        ))}
      </div>

      {/* Live Chart */}
      <div className="mb-2 text-sm text-white/50">
        Live Requests/sec & Latency
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <XAxis
            dataKey="time"
            tick={{ fill: "#ffffff50", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "#ffffff50", fontSize: 10 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "#1e1e2e",
              border: "1px solid #ffffff20",
              borderRadius: 8,
              color: "#fff",
            }}
          />
          <Line
            type="monotone"
            dataKey="rps"
            stroke="#6366f1"
            strokeWidth={2}
            dot={false}
            name="Requests/sec"
          />
          <Line
            type="monotone"
            dataKey="latency"
            stroke="#ec4899"
            strokeWidth={2}
            dot={false}
            name="Latency (ms)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}