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