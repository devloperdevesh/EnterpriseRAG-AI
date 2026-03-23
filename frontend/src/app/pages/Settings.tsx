import ThemeToggle from "../../components/ThemeToggle";

export default function Settings() {
  return (
    <div className="glass p-6">

      <h2 className="text-xl mb-4">Settings</h2>

      <div className="flex justify-between items-center">
        <p>Dark Mode</p>
        <ThemeToggle />
      </div>

    </div>
  );
}