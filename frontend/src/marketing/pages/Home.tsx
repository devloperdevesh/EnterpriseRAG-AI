import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import Architecture from "../components/Architecture";
import BenchmarkPreview from "../components/BenchmarkPreview";
import Impact from "../components/Impact";
import TechStack from "../components/TechStack";
import CTA from "./CTA";
import Footer from "../components/Footer";

export default function Home() {
  return (
    <main className="w-full min-h-screen bg-black text-white overflow-hidden">
      {/* Navigation */}
      <Navbar />

      {/* Hero Section */}
      <Hero />

      {/* Architecture Showcase */}
      <Architecture />

      {/* Performance Benchmarks */}
      <BenchmarkPreview />

      {/* System Impact / Metrics */}
      <Impact />

      {/* Technology Stack */}
      <TechStack />

      {/* Final CTA */}
      <CTA />

      {/* Footer */}
      <Footer />
    </main>
  );
}
