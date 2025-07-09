import React, { useContext } from "react";
import ChatIA from "./ChatIA";
import PanelSubida from "./PanelSubida";
import { ADNIAContext } from "./ADNIAContext";

function PanelFiscal() {
  const { sugerencia, memoriaLarga } = useContext(ADNIAContext);
  const volver = () => window.location.href = "/modulos";
  return (
    <div style={{
      maxWidth: "1080px", margin: "30px auto", padding: "32px 10px 100px 10px",
      background: "rgba(12,18,27,0.97)", borderRadius: "18px",
      boxShadow: "0 0 48px #00ffd955", position: "relative"
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <h2 style={{ color: "#00ffd9", fontWeight: "bold", fontSize: "2.3rem", textShadow: "0 0 16px #00ffd9" }}>
          Panel Fiscal
        </h2>
        <button onClick={volver} style={{
          background: "#00ffd9", color: "#000", padding: "12px 22px",
          border: "none", borderRadius: "10px", fontWeight: "bold", fontSize: "1.08rem",
          cursor: "pointer", boxShadow: "0 0 12px #00ffd9"
        }}>← Volver</button>
      </div>
      <p style={{ color: "#fff", fontSize: "1.13rem", marginBottom: "28px", fontStyle: "italic" }}>
        Optimiza declaraciones, deducciones y resuelve cualquier inspección, recurso o duda fiscal con ADNIA.
      </p>
      <div style={{
        background: "#101924", borderRadius: "15px", padding: "22px 18px", marginBottom: "22px",
        boxShadow: "0 0 16px #00ffd977"
      }}>
        <ChatIA modulo="Fiscal" />
      </div>
      {sugerencia && (
        <div style={{
          background: "#162d2d", color: "#7efcd9", padding: "18px 14px", borderRadius: "12px",
          marginBottom: "18px", fontWeight: "bold", fontSize: "1.1rem",
          border: "1px solid #00ffd9", boxShadow: "0 0 8px #00ffd955"
        }}>
          💡 {sugerencia}
        </div>
      )}
      <div style={{
        background: "#111d25", borderRadius: "15px", padding: "24px 18px",
        marginBottom: "0", boxShadow: "0 0 16px #00ffd966"
      }}>
        <PanelSubida modulo="Fiscal" />
      </div>
      {memoriaLarga && memoriaLarga.length > 0 && (
        <div style={{
          position: "absolute", bottom: "16px", right: "24px",
          color: "#00ffd9", opacity: 0.7, fontSize: "1rem"
        }}>
          🧠 Memoria activa ({memoriaLarga.length} entradas)
        </div>
      )}
    </div>
  );
}
export default PanelFiscal;
