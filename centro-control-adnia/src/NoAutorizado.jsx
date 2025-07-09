import React from "react";

export default function NoAutorizado() {
  return (
    <div style={{
      minHeight: "100vh",
      background: "#191e29",
      color: "#ff4c6e",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      flexDirection: "column"
    }}>
      <h1 style={{ fontSize: "2.3rem", fontWeight: "bold" }}>⛔ Acceso denegado</h1>
      <p style={{ fontSize: "1.13rem", color: "#ffe1ea" }}>
        No tienes permisos para entrar aquí.<br />Contacta con ADNIA si necesitas acceso especial.
      </p>
      <a href="/" style={{
        marginTop: "24px",
        color: "#00ffd9",
        fontWeight: "bold",
        textDecoration: "underline"
      }}>
        Volver al inicio
      </a>
    </div>
  );
}
