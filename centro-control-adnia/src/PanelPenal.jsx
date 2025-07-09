import React, { useContext, useEffect } from "react";
import { ADNIAContext } from "./ADNIAContext";
import { useNavigate } from "react-router-dom";

function PanelCivil() {
  const { usuario, setUsuario, setRol, setPais } = useContext(ADNIAContext);
  const navigate = useNavigate();

  // Protección de sesión: Si no hay sesión, te echa
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

  // LOGOUT seguro (puedes usar este handler en tu menú o botón logout)
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

  // Tu UI ADNIA, aquí metes lo que quieras para civil:
  return (
    <div style={{ padding: 40, color: "#00ffd9", minHeight: "100vh" }}>
      <h2 style={{ fontWeight: "bold", fontSize: 32 }}>Panel Civil ADNIA</h2>
      <p>
        Bienvenido/a, <b>{usuario}</b>. Aquí puedes gestionar expedientes civiles, demandas, recursos y más.
      </p>

      {/* Botón de logout ejemplo */}
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

      {/* Aquí va tu contenido civil, tus formularios, tablas, chat IA, etc */}
      <div style={{ marginTop: 32 }}>
        {/* Ejemplo de módulo, elimina o personaliza */}
        <h3>Acciones civiles disponibles</h3>
        <ul>
          <li>Redactar demanda civil</li>
          <li>Consultar jurisprudencia civil</li>
          <li>Gestionar documentación</li>
        </ul>
      </div>
    </div>
  );
}

export default PanelCivil;
