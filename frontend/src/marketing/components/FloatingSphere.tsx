import { Canvas } from "@react-three/fiber";

function Sphere() {
  return (
    <mesh>
      <sphereGeometry args={[1, 32, 32]} />
      <meshStandardMaterial color="blue" />
    </mesh>
  );
}

export default function FloatingSphere() {
  return (
    <Canvas style={{ height: 200 }}>
      <ambientLight />
      <Sphere />
    </Canvas>
  );
}