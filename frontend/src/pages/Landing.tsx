import Navbar from "../components/layout/Navbar";
import Footer from "../components/layout/Footer";

import Hero from "../components/landing/Hero";
import Architecture from "../components/landing/Architecture";
import BenchmarkPreview from "../components/landing/BenchmarkPreview";
import CTA from "../components/landing/CTA";

export default function Landing() {
  return (
    <main
      className="
        min-h-screen
        bg-black
        text-white
        overflow-x-hidden
      "
    >
      {/* =========================
          NAVIGATION
      ========================= */}
      <Navbar />

      {/* =========================
          HERO SECTION
      ========================= */}
      <Hero />

      {/* =========================
          DISTRIBUTED ARCHITECTURE
      ========================= */}
      <Architecture />

      {/* =========================
          PERFORMANCE METRICS
      ========================= */}
      <BenchmarkPreview />

      {/* =========================
          FINAL CTA
      ========================= */}
      <CTA />

      {/* =========================
          FOOTER
      ========================= */}
      <Footer />
    </main>
  );
}
