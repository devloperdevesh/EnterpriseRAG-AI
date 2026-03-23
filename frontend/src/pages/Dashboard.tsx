export default function Dashboard() {
  return (
    <div className="grid grid-cols-3 gap-6">

      <div className="glass">
        <h2>Documents</h2>
        <p>102,348</p>
      </div>

      <div className="glass">
        <h2>Requests/sec</h2>
        <p>8,742</p>
      </div>

      <div className="glass">
        <h2>Latency</h2>
        <p>~420ms</p>
      </div>

    </div>
  );
}