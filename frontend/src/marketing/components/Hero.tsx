import FloatingSphere from "./FloatingSphere";
import ParticlesBg from "./ParticlesBg";

export default function Hero() {
  return (
    <div className="relative text-center py-24">

      <ParticlesBg />
      <FloatingSphere />

      <h1 className="text-6xl font-bold">
        AI-Powered Document Intelligence
      </h1>

      <p className="mt-4 text-gray-400">
        Process 100K+ documents with sub-second AI retrieval
      </p>

      <div className="mt-6 flex justify-center gap-4">
        <button className="bg-blue-500 px-6 py-2 rounded">
          Start Free Trial
        </button>

        <button className="border px-6 py-2 rounded">
          View Demo
        </button>
      </div>

    </div>
  );
}