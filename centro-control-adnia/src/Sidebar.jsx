import React from "react";

// Puedes sustituir estos iconos SVG por los que más te gusten de lucide-react o fontawesome
const iconStyle = { width: 28, height: 28, marginBottom: 7, filter: "drop-shadow(0 0 5px #00ffe7a7)" };

const sidebarStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  height: "100vh",
  width: 86,
  background: "linear-gradient(160deg, #0a1828 80%, #00ffd9 180%)",
  boxShadow: "0 0 30px 0 #00ffd940",
  zIndex: 999,
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  paddingTop: 34,
  gap: 20,
};

const avatarStyle = {
  background: "radial-gradient(circle at 38% 20%, #00ffd9 85%, #1c4440 100%)",
  width: 56,
  height: 56,
  borderRadius: "50%",
  marginBottom: 35,
  boxShadow: "0 0 14px 6px #00ffd9bb",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  fontSize: 33,
  color: "#fff",
  fontWeight: 800,
  border: "3px solid #43fff1"
};

const menuItemStyle = (active) => ({
  color: active ? "#00ffd9" : "#e8ffff",
  background: active ? "rgba(0,255,217,0.07)" : "transparent",
  borderRadius: "13px",
  padding: "10px 2px",
  fontWeight: "bold",
  fontSize: "1.04em",
  textAlign: "center",
  cursor: "pointer",
  marginBottom: 7,
  transition: "all 0.18s",
  boxShadow: active ? "0 0 8px #00ffd9" : "none"
});

export default function Sidebar({ active, onNavigate }) {
  // Puedes expandir o cambiar las rutas según tus paneles
  const menu = [
    { key: "dashboard", label: "Panel", icon: <span style={iconStyle}>🏠</span> },
    { key: "fiscal", label: "Fiscal", icon: <span style={iconStyle}>📊</span> },
    { key: "laboral", label: "Laboral", icon: <span style={iconStyle}>💼</span> },
    { key: "penal", label: "Penal", icon: <span style={iconStyle}>⚖️</span> },
    { key: "auditoria", label: "Auditoría", icon: <span style={iconStyle}>🔎</span> },
    { key: "documentos", label: "Documentos", icon: <span style={iconStyle}>📁</span> },
    { key: "boe", label: "BOE/AEAT", icon: <span style={iconStyle}>📜</span> },
    { key: "blockchain", label: "Blockchain", icon: <span style={iconStyle}>🔗</span> },
    { key: "ia", label: "Copiloto IA", icon: <span style={iconStyle}>🤖</span> },
    // Más...
  ];

  // Si quieres un handler global para navegación (React Router)
  const handleClick = (key) => {
    if (onNavigate) onNavigate(key);
    // Si usas React Router v6+, puedes usar navigate(`/fiscal`) etc.
  };

  return (
    <nav style={sidebarStyle}>
      <div style={avatarStyle}>
        <span role="img" aria-label="adnia-logo">🧠</span>
      </div>
      {menu.map((item) => (
        <div
          key={item.key}
          style={menuItemStyle(active === item.key)}
          onClick={() => handleClick(item.key)}
          title={item.label}
        >
          {item.icon}
          <div style={{ fontSize: 13, letterSpacing: "1.5px" }}>{item.label}</div>
        </div>
      ))}
      {/* Botón de logout */}
      <div
        style={{
          marginTop: "auto",
          marginBottom: 18,
          color: "#ffabab",
          fontWeight: "bold",
          fontSize: "1.04em",
          cursor: "pointer"
        }}
        onClick={() => {
          localStorage.clear();
          fetch("http://localhost:3002/logout", { method: "POST", credentials: "include" }).then(() => window.location.href = "/");
        }}
      >
        <span style={iconStyle}>🚪</span>
        <div style={{ fontSize: 13 }}>Salir</div>
      </div>
    </nav>
  );
}
