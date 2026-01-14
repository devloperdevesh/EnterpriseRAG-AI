import { useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";


export default function Login({ onSwitchToSignup }: any) {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const submit = async () => {
    setError("");
    try {
      const res = await api.post("/auth/login", {
        email,
        password
      });
      login(res.data.access_token);
    } catch {
      setError("Invalid email or password");
    }
  };

  return (
    <div style={styles.card}>
      <h2 style={styles.title}>EnterpriseRAG AI</h2>

      <input
        placeholder="Email"
        value={email}
        onChange={(e)=>setEmail(e.target.value)}
        style={styles.input}
      />

      <input
        placeholder="Password"
        type="password"
        value={password}
        onChange={(e)=>setPassword(e.target.value)}
        style={styles.input}
      />

      {error && <p style={{color:"red"}}>{error}</p>}

      <button onClick={submit} style={styles.button}>
        Login
      </button>

      <p style={{marginTop:15}}>
        New user?{" "}
        <span style={styles.link} onClick={onSwitchToSignup}>
          Create account
        </span>
      </p>
    </div>
  );
}

const styles = {
  card:{
    width:420,
    margin:"120px auto",
    padding:32,
    borderRadius:16,
    background:"#ffffff",
    boxShadow:"0 15px 60px rgba(0,0,0,0.12)",
    textAlign:"center" as const,
    fontFamily:"Inter,system-ui"
  },
  title:{fontSize:22,fontWeight:600,marginBottom:20},
  input:{
    width:"100%",
    padding:12,
    marginBottom:14,
    borderRadius:8,
    border:"1px solid #ddd",
    fontSize:14
  },
  button:{
    width:"100%",
    padding:12,
    borderRadius:10,
    border:"none",
    background:"linear-gradient(90deg,#8A2BE2,#007BFF)",
    color:"white",
    fontWeight:600,
    cursor:"pointer"
  },
  link:{color:"#007BFF",cursor:"pointer"}
};
