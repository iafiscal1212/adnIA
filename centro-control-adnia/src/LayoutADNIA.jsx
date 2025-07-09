import React, { useState, useContext } from "react";
import { ADNIAContext } from "./ADNIAContext";
import "./App.css";

function LayoutADNIA({ children }) {
  const [horizontal, setHorizontal] = useState(true);
  const { usuario, logout } = useContext(ADNIAContext);

  return (
    <div className="app-container" style={{
      minHeight: "100vh",
      backgroundColor: "#0b0f1a",
      color: "#ffffff",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      padding: "40px 20px",
    }}>
      {/* Cabecera con usuario y logout */}
      {usuario && (
        <div style={{
          width: "100%",
          display: "flex",
          justifyContent: "flex-end",
          alignItems: "center",
          marginBottom: "18px"
        }}>
          <span style={{ color: "#00ffd9", marginRight: "22px", fontWeight: "bold" }}>
            {usuario}
          </span>
          <button
            className="adnia-btn"
            style={{ background: "#ff0055", color: "#fff", border: "none", borderRadius: "8px", padding: "8px 22px", fontWeight: "bold", cursor: "pointer" }}
            onClick={logout}
          >
            Cerrar sesión
          </button>
        </div>
      )}

      <main
        className={`${horizontal ? "flex-row" : "flex-col"} flex flex-wrap gap-6 justify-center items-start w-full max-w-6xl`}
        style={{ marginBottom: "10px" }}
      >
        {children}
      </main>
    </div>
  );
}

export default LayoutADNIA;
