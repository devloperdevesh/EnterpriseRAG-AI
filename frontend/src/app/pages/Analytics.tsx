import { LineChart, Line, XAxis, YAxis } from "recharts";

const data = [
  { name: "Day1", queries: 400 },
  { name: "Day2", queries: 800 },
];

export default function Analytics() {
  return (
    <LineChart width={400} height={200} data={data}>
      <XAxis dataKey="name" />
      <YAxis />
      <Line type="monotone" dataKey="queries" />
    </LineChart>
  );
}
export default function Analytics() {
  const stats = {
    users: 842,
    requests: 12450,
    latency: "480ms",
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold">System Metrics</h2>

      <div className="grid grid-cols-3 gap-6 mt-4">

        <div className="glass p-4">
          <p>Active Users</p>
          <h3 className="text-2xl">{stats.users}</h3>
        </div>

        <div className="glass p-4">
          <p>Requests</p>
          <h3 className="text-2xl">{stats.requests}</h3>
        </div>

        <div className="glass p-4">
          <p>Latency</p>
          <h3 className="text-2xl">{stats.latency}</h3>
        </div>

      </div>
    </div>
  );
}