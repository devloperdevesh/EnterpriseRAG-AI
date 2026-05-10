import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const chartData = [
  { name: "Mon", queries: 320 },
  { name: "Tue", queries: 540 },
  { name: "Wed", queries: 780 },
  { name: "Thu", queries: 620 },
  { name: "Fri", queries: 910 },
  { name: "Sat", queries: 1040 },
  { name: "Sun", queries: 860 },
];

export default function Analytics() {
  const stats = [
    {
      title: "Active Users",
      value: "842",
    },
    {
      title: "Requests",
      value: "12,450",
    },
    {
      title: "p95 Latency",
      value: "480ms",
    },
    {
      title: "Error Rate",
      value: "<1%",
    },
  ];

  return (
    <div className="w-full min-h-screen bg-black text-white p-8">
      {/* Header */}
      <div className="mb-12">
        <p className="uppercase tracking-[0.3em] text-sm text-neutral-500 mb-4">
          Observability Dashboard
        </p>

        <h1 className="text-5xl font-bold">System Analytics</h1>

        <p className="text-neutral-400 mt-4 max-w-2xl leading-relaxed">
          Realtime infrastructure metrics, throughput monitoring, latency
          visualization, and distributed system observability.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 mb-12">
        {stats.map((item, index) => (
          <div
            key={index}
            className="bg-neutral-900 border border-neutral-800 rounded-3xl p-6"
          >
            <p className="text-sm uppercase tracking-wider text-neutral-500 mb-3">
              {item.title}
            </p>

            <h2 className="text-4xl font-bold">{item.value}</h2>
          </div>
        ))}
      </div>

      {/* Chart */}
      <div className="bg-neutral-900 border border-neutral-800 rounded-3xl p-8">
        <div className="mb-8">
          <h2 className="text-2xl font-semibold">Request Throughput</h2>

          <p className="text-neutral-400 mt-2">
            Weekly request volume across the distributed inference pipeline.
          </p>
        </div>

        <div className="w-full h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid stroke="#262626" />

              <XAxis dataKey="name" stroke="#737373" />

              <YAxis stroke="#737373" />

              <Tooltip />

              <Line
                type="monotone"
                dataKey="queries"
                stroke="#ffffff"
                strokeWidth={3}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
