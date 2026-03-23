import { useAppStore } from "../../store/useAppStore";

export default function Profile() {
  const { user } = useAppStore();

  return (
    <div className="glass p-6">

      <h2 className="text-xl mb-4">Profile</h2>

      <p><b>Name:</b> {user?.name || "Devesh"}</p>
      <p><b>Email:</b> {user?.email || "user@mail.com"}</p>

    </div>
  );
}