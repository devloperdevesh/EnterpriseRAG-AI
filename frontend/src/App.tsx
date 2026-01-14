import Login from "./auth/Login";
import Signup from "./auth/Signup";
import Dashboard from "./pages/Dashboard";
import { useAuth } from "./context/AuthContext";
import { useState } from "react";

export default function App() {
  const { token } = useAuth();
  const [page, setPage] = useState<"login"|"signup">("login");

  if (token) return <Dashboard />;

  if (page === "signup")
    return <Signup onBack={()=>setPage("login")} />;

  return <Login onSwitchToSignup={()=>setPage("signup")} />;
}
