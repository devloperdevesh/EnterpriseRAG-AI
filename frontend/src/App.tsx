import AppRoutes from "./routes/AppRoutes";
import ParticlesBg from "./marketing/components/ParticlesBg";

export default function App() {
  return (
    <div className="app-root">
      {/* Global Background */}
      <ParticlesBg />

      {/* Gradient overlay */}
      <div className="gradient-bg" />

      {/* Main App */}
      <AppRoutes />
    </div>
  );
}