import React, { useContext, useEffect } from "react";
import { ADNIAContext } from "./ADNIAContext";
import { useNavigate } from "react-router-dom";

function PanelSocial() {
  const { usuario, setUsuario, setRol, setPais } = useContext(ADNIAContext);
  const navigate = useNavigate();

  useEffect(() => {
    fetch("http://localhost:3002/dashboard", {
      method: "GET",
      credentials: "include"
    })
      .then(res => {
        if (res.status === 401) {
          localStorage.removeItem("usuario");
          localStorage.removeItem("rol");
          localStorage.removeItem("pais");
          setUsuario("");
          setRol("cliente");
          setPais("España");
          navigate("/");
        }
      });
  }, [navigate, setUsuario, setRol, setPais]);

  const handleLogout = async () => {
    await fetch("http://localhost:3002/logout", { method: "POST", credentials: "include" });
    localStorage.removeItem("usuario");
    localStorage.removeItem("rol");
    localStorage.removeItem("pais");
    setUsuario("");
    setRol("cliente");
    setPais("España");
    navigate("/");
  };

  return (
    <div style={{ padding: 40, color: "#00ffd9", minHeight: "100vh" }}>
      <h2 style={{ fontWeight: "bold", fontSize: 32 }}>Panel Social ADNIA</h2>
      <p>
        Bienvenido/a, <b>{usuario}</b>. Aquí puedes gestionar expedientes sociales, despidos, prestaciones, etc.
      </p>
      <button
        style={{
          background: "#ff3c48",
          color: "#fff",
          border: "none",
          padding: "12px 32px",
          borderRadius: 10,
          fontWeight: "bold",
          margin: "20px 0",
          boxShadow: "0 0 18px #ff3c48cc"
        }}
        onClick={handleLogout}
      >
        Cerrar sesión
      </button>

      <div style={{ marginTop: 32 }}>
        <h3>Acciones sociales disponibles</h3>
        <ul>
          <li>Redactar demanda laboral</li>
          <li>Gestionar recursos sociales</li>
          <li>Consultar normativa laboral</li>
        </ul>
      </div>
    </div>
  );
}

export default PanelSocial;
