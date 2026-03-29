import Particles from "react-tsparticles";

export default function ParticlesBg() {
  return (
    <Particles
      options={{
        particles: {
          number: { value: 40 },
          size: { value: 2 },
          move: { speed: 1 },
          opacity: { value: 0.3 },
        },
      }}
      className="absolute inset-0 -z-10"
    />
  );
}