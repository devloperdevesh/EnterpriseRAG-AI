import { useState } from "react";
import { api } from "../api/client";

export default function Signup({ onBack }: any) {
  const [email,setEmail] = useState("");
  const [password,setPassword] = useState("");
  const [message,setMessage] = useState("");

  const submit = async () => {
    try {
      const res = await api.post("/auth/signup",{email,password});
      setMessage(res.data.message);
    } catch (err:any) {
      setMessage(err.response?.data?.detail || "Signup failed");
    }
  };

  return (
    <div style={styles.card}>
      <h2>Create Account</h2>

      <input placeholder="Email" value={email}
        onChange={(e)=>setEmail(e.target.value)}
        style={styles.input}/>

      <input placeholder="Password" type="password"
        value={password}
        onChange={(e)=>setPassword(e.target.value)}
        style={styles.input}/>

      <button onClick={submit} style={styles.button}>
        Sign Up
      </button>

      <p style={{marginTop:15}}>
        <span style={styles.link} onClick={onBack}>
          Back to Login
        </span>
      </p>

      {message && <p>{message}</p>}
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
    textAlign:"center" as const
  },
  input:{
    width:"100%",
    padding:12,
    marginBottom:14,
    borderRadius:8,
    border:"1px solid #ddd"
  },
  button:{
    width:"100%",
    padding:12,
    borderRadius:10,
    border:"none",
    background:"linear-gradient(90deg,#8A2BE2,#007BFF)",
    color:"white",
    fontWeight:600
  },
  link:{color:"#007BFF",cursor:"pointer"}
};
