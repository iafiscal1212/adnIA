import React, { useState } from "react";
import { GoogleLogin } from "@react-oauth/google";
import { BACKEND_URL } from "./config";

function Login({ onLogin }) {
  const [usuario, setUsuario] = useState("");
  const [clave, setClave] = useState("");
  const [registrando, setRegistrando] = useState(false);
  const [rol, setRol] = useState("cliente");
  const [pais, setPais] = useState("España");
  const [error, setError] = useState("");

  // Alta usuario
  const registrar = async () => {
    setError("");
    const res = await fetch(`${BACKEND_URL}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, clave, rol, pais }),
      credentials: "include"
    });
    const data = await res.json();
    if (data.ok) {
      setRegistrando(false);
      setUsuario("");
      setClave("");
      alert("Usuario registrado, ahora puedes acceder.");
    } else {
      setError(data.error);
    }
  };

  // Login usuario/clave
  const login = async () => {
    setError("");
    const res = await fetch(`${BACKEND_URL}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ usuario, clave }),
      credentials: "include"
    });
    const data = await res.json();
    if (data.ok) {
      onLogin(data);
    } else {
      setError(data.error);
    }
  };

  // Login con Google
  const loginGoogle = async (credentialResponse) => {
    setError("");
    const res = await fetch(`${BACKEND_URL}/login-google`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ token_id: credentialResponse.credential }),
      credentials: "include"
    });
    const data = await res.json();
    if (data.ok) {
      onLogin(data);
    } else {
      setError(data.error);
    }
  };

  return (
    <div style={{
      minHeight: "100vh", display: "flex", flexDirection: "column",
      alignItems: "center", justifyContent: "center", background: "#101826"
    }}>
      <div style={{
        background: "#111a23", borderRadius: "18px", boxShadow: "0 0 44px #00ffd988",
        padding: "48px 36px", minWidth: "340px", color: "#00ffd9"
      }}>
        <h1 style={{ fontWeight: 800, fontSize: "2.2rem", marginBottom: "12px" }}>ADNIA Login</h1>
        <p style={{ color: "#fff", fontStyle: "italic", marginBottom: 24 }}>
          Accede o regístrate para disfrutar de la IA jurídica más disruptiva.
        </p>

        {registrando ? (
          <>
            <input type="text" placeholder="Usuario (email)" value={usuario} onChange={e => setUsuario(e.target.value)}
              style={inputEstilo} />
            <input type="password" placeholder="Clave" value={clave} onChange={e => setClave(e.target.value)}
              style={inputEstilo} />
            <select value={rol} onChange={e => setRol(e.target.value)} style={inputEstilo}>
              <option value="cliente">Cliente</option>
              <option value="asesoría">Asesoría</option>
              <option value="admin">Admin</option>
            </select>
            <input type="text" placeholder="País" value={pais} onChange={e => setPais(e.target.value)}
              style={inputEstilo} />
            <button onClick={registrar} style={botonEstilo}>Registrar</button>
            <button onClick={() => setRegistrando(false)} style={botonEstiloSec}>Volver a Login</button>
          </>
        ) : (
          <>
            <input type="text" placeholder="Usuario o email" value={usuario} onChange={e => setUsuario(e.target.value)}
              style={inputEstilo} />
            <input type="password" placeholder="Clave" value={clave} onChange={e => setClave(e.target.value)}
              style={inputEstilo} />
            <button onClick={login} style={botonEstilo}>Acceder</button>
            <button onClick={() => setRegistrando(true)} style={botonEstiloSec}>Crear cuenta</button>
            <div style={{ margin: "14px 0" }}>
              <GoogleLogin
                onSuccess={loginGoogle}
                onError={() => setError("Error Google Login")}
              />
            </div>
          </>
        )}
        {error && <div style={{ color: "#ff4848", marginTop: "8px" }}>{error}</div>}
      </div>
    </div>
  );
}

const inputEstilo = {
  width: "100%",
  padding: "10px",
  marginBottom: "14px",
  borderRadius: "8px",
  border: "1px solid #00ffd9",
  backgroundColor: "#111c24",
  color: "#00ffd9"
};
const botonEstilo = {
  width: "100%",
  padding: "12px", background: "#00ffd9", color: "#000", fontWeight: "bold",
  border: "none", borderRadius: "8px", cursor: "pointer", marginBottom: "10px"
};
const botonEstiloSec = {
  width: "100%", padding: "10px", background: "#222c36", color: "#00ffd9",
  fontWeight: "bold", border: "none", borderRadius: "8px", cursor: "pointer", marginBottom: "8px"
};

export default Login;
