import React, { useContext, useEffect, useState } from "react";
import { ADNIAContext } from "./ADNIAContext";
import { useNavigate } from "react-router-dom";

function PanelAdmin() {
  // Contexto global ADNIA
  const { usuario, rol, setUsuario, setRol, setPais } = useContext(ADNIAContext);
  const navigate = useNavigate();

  // (Opcional) Ejemplo de estado local si necesitas
  const [usuarios, setUsuarios] = useState([]);
  const [cargando, setCargando] = useState(true);

  // Protección de sesión y solo admin
  useEffect(() => {
    fetch("http://localhost:3002/dashboard", {
      method: "GET",
      credentials: "include"
    })
      .then(res => {
        if (res.status === 401 || rol !== "admin") {
          localStorage.removeItem("usuario");
          localStorage.removeItem("rol");
          localStorage.removeItem("pais");
          setUsuario("");
          setRol("cliente");
          setPais("España");
          navigate("/");
        }
      });
  }, [navigate, rol, setUsuario, setRol, setPais]);

  // Ejemplo: cargar lista de usuarios (solo admin)
  useEffect(() => {
    if (rol === "admin") {
      fetch("http://localhost:3002/usuarios", {
        method: "GET",
        credentials: "include"
      })
        .then(res => res.json())
        .then(data => {
          setUsuarios(data.usuarios || []);
          setCargando(false);
        });
    }
  }, [rol]);

  // LOGOUT seguro
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

  // --- Render del panel ---
  return (
    <div style={{ padding: 40, color: "#00ffd9", minHeight: "100vh" }}>
      <h2 style={{ fontWeight: "bold", fontSize: 32 }}>Panel de Administración ADNIA</h2>
      <p>
        Bienvenido/a, <b>{usuario}</b>. Solo los administradores pueden ver este panel.
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
        <h3>Gestión de usuarios (ejemplo)</h3>
        {cargando ? (
          <p>Cargando usuarios...</p>
        ) : (
          <ul>
            {usuarios.length === 0 && <li>No hay usuarios registrados.</li>}
            {usuarios.map((u, idx) => (
              <li key={idx}>
                <b>{u.usuario}</b> - Rol: {u.rol} - País: {u.pais}
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Aquí va tu lógica adicional de gestión, tablas, formularios, etc */}
    </div>
  );
}

export default PanelAdmin;
