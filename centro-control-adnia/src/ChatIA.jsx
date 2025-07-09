import React, { useContext, useState } from "react";
import { ADNIAContext } from "./ADNIAContext";

function ChatIA({ modulo }) {
  const {
    usuario, rol, pais,
    memoriaCorta, setMemoriaCorta,
    memoriaLarga,
    guardarEnMemoriaLarga,
    documentoTexto,
    sugerencia,
    historial
  } = useContext(ADNIAContext);

  const [input, setInput] = useState("");
  const [cargando, setCargando] = useState(false);

  // Envia el mensaje al backend, usando TODO el contexto
  const enviarMensaje = async () => {
    if (!input.trim()) return;
    setCargando(true);

    // Añade el mensaje del usuario a la memoriaCorta antes de enviar
    const nuevaMemoriaCorta = [...memoriaCorta, { rol: "user", texto: input }];
    setMemoriaCorta(nuevaMemoriaCorta);
    guardarEnMemoriaLarga({ rol: "user", texto: input });

    try {
      const res = await fetch("http://localhost:3002/resolver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        credentials: "include", // SIEMPRE
          usuario,
          rol,
          pais,
          modulo: modulo || "General",
          historial: nuevaMemoriaCorta,
          memoriaLarga,
          sugerencia,
          documentoTexto,
          pregunta: input,
          MCP: true
        })
      });

      const data = await res.json();
      setMemoriaCorta([...nuevaMemoriaCorta, { rol: "ia", texto: data.respuesta }]);
      guardarEnMemoriaLarga({ rol: "ia", texto: data.respuesta });
    } catch (err) {
      setMemoriaCorta([...nuevaMemoriaCorta, { rol: "ia", texto: "❌ Error conectando con ADNIA." }]);
    }
    setInput("");
    setCargando(false);
  };

  return (
    <div style={{
      background: "#111a23",
      borderRadius: "16px",
      padding: "18px",
      margin: "16px 0"
    }}>
      {/* Mensajes */}
      {memoriaCorta.map((msg, i) => (
        <div key={i} style={{
          background: msg.rol === "user" ? "#203145" : "#183c4c",
          color: msg.rol === "user" ? "#fff" : "#00ffd9",
          padding: "10px 16px",
          borderRadius: "12px",
          margin: "6px 0",
          textAlign: msg.rol === "user" ? "right" : "left"
        }}>{msg.texto}</div>
      ))}
      {/* Sugerencia automática */}
      {sugerencia && (
        <div style={{
          background: "#223044",
          color: "#00ffd9",
          borderRadius: "10px",
          padding: "12px",
          margin: "8px 0",
          fontStyle: "italic"
        }}>{sugerencia}</div>
      )}
      {/* Input */}
      <div style={{ display: "flex", marginTop: "12px" }}>
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          style={{
            flex: 1, borderRadius: "10px", border: "1px solid #00ffd9",
            padding: "10px", background: "#121d29", color: "#00ffd9"
          }}
          placeholder="Escribe una consulta para ADNIA..."
          onKeyDown={e => { if (e.key === "Enter") enviarMensaje(); }}
          disabled={cargando}
        />
        <button
          onClick={enviarMensaje}
          disabled={cargando}
          style={{
            marginLeft: "8px", background: "#00ffd9", color: "#121d29",
            border: "none", borderRadius: "10px", fontWeight: "bold", padding: "10px 18px"
          }}>
          {cargando ? "Enviando..." : "Enviar"}
        </button>
      </div>
    </div>
  );
}

export default ChatIA;
