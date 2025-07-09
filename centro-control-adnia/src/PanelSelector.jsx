import React from "react";
import { useNavigate } from "react-router-dom";

// FUNCIÓN LOGOUT
async function handleLogout() {
  await fetch("https://adnia.online/logout", { method: "POST", credentials: "include" });
  window.location.href = "/"; // o donde esté tu Login
}

function PanelSelector() {
  const navigate = useNavigate();

  const irAModulo = (ruta) => {
    navigate(ruta);
  };

  const botones = [
    { nombre: "Fiscal", ruta: "/fiscal", color: "#00ffd9" },
    { nombre: "Penal", ruta: "/penal", color: "#ff7f7f" },
    { nombre: "Civil", ruta: "/civil", color: "#00aaff" },
    { nombre: "Administrativo", ruta: "/administrativo", color: "#ffaa00" },
    { nombre: "Social", ruta: "/social", color: "#66ff99" },
    { nombre: "Admin", ruta: "/admin", color: "#cc00ff" },
  ];

  return (
    <div style={estilos.contenedor}>
      <div style={estilos.encabezado}>
        <h1 style={estilos.tituloPrincipal}>
          📂 ADNIA — Módulo Jurídico
        </h1>
        <p style={estilos.lema}>
          “Aquí no obedecemos a la ignorancia disfrazada de ley.”
        </p>
        <p style={estilos.descripcion}>
          Selecciona un módulo jurídico para interactuar con ADNIA en su dominio especializado.
        </p>
      </div>

      <h2 style={estilos.titulo}>Selecciona un módulo jurídico</h2>
      <div style={estilos.botonera}>
        {botones.map((modulo, i) => (
          <button
            key={i}
            onClick={() => irAModulo(modulo.ruta)}
            style={{ ...estilos.boton, backgroundColor: modulo.color }}
          >
            {modulo.nombre}
          </button>
        ))}
      </div>

      {/* BOTÓN DE CERRAR SESIÓN */}
      <div style={{ marginTop: "60px", textAlign: "center" }}>
        <button
          onClick={handleLogout}
          style={{
            backgroundColor: "#ff5050",
            color: "#fff",
            fontWeight: "bold",
            border: "none",
            padding: "15px 44px",
            borderRadius: "10px",
            fontSize: "1.15rem",
            cursor: "pointer",
            boxShadow: "0 0 10px #ff505088",
            marginTop: "10px",
            letterSpacing: "1px"
          }}
        >
          Cerrar sesión
        </button>
      </div>
    </div>
  );
}

const estilos = {
  contenedor: {
    padding: "60px 20px",
    textAlign: "center",
    color: "#ffffff",
    backgroundColor: "#0e0f11",
  },
  encabezado: {
    textAlign: "center",
    marginBottom: "40px",
  },
  tituloPrincipal: {
    color: "#00ffd9",
    fontSize: "2.5rem",
    textShadow: "0 0 10px #00ffd9",
    marginBottom: "10px",
  },
  lema: {
    fontStyle: "italic",
    color: "#ccc",
    marginBottom: "10px",
  },
  descripcion: {
    maxWidth: "900px",
    margin: "0 auto",
    color: "#ccc",
    fontSize: "1rem",
  },
  titulo: {
    fontSize: "2rem",
    fontWeight: "bold",
    textAlign: "center",
    color: "#00ffd9",
    marginTop: "20px",
    marginBottom: "30px",
  },
  botonera: {
    display: "flex",
    flexWrap: "wrap",
    gap: "20px",
    justifyContent: "center",
  },
  boton: {
    padding: "20px 30px",
    fontSize: "18px",
    border: "none",
    borderRadius: "10px",
    color: "#000",
    fontWeight: "bold",
    cursor: "pointer",
    minWidth: "180px",
    transition: "transform 0.2s",
  },
};

export default PanelSelector;
