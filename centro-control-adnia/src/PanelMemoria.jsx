import React, { useState, useRef, useEffect, useContext } from "react";
import { ADNIAContext } from "./ADNIAContext";
import { useNavigate } from "react-router-dom";

function PanelMemoria() {
  const {
    memoriaCorta,
    registrarEnMemoria,
    usuarioInactivo,
    setUsuarioInactivo,
  } = useContext(ADNIAContext);
  const [entrada, setEntrada] = useState("");
  const [historial, setHistorial] = useState([]);
  const chatEndRef = useRef(null);
  const navigate = useNavigate();

  // Protección de sesión ADNIA
  useEffect(() => {
    fetch("http://localhost:3002/dashboard", {
      method: "GET",
      credentials: "include"
    }).then(res => {
      if (res.status === 401) {
        localStorage.removeItem("usuario");
        localStorage.removeItem("rol");
        localStorage.removeItem("pais");
        navigate("/");
      }
    });
  }, [navigate]);

  const enviarMensaje = async () => {
    if (!entrada.trim()) return;

    const nuevoMensaje = { texto: entrada, emisor: "usuario" };
    setHistorial((prev) => [...prev, nuevoMensaje]);
    registrarEnMemoria(nuevoMensaje);
    setEntrada("");

    try {
      const res = await fetch("http://localhost:3002/resolver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pregunta: entrada,
          categoria: "general",
          MCP: true,
        credentials: "include"
        }),
      });

      const data = await res.json();
      const respuestaIA = {
        texto: data.respuesta || "Sin respuesta de ADNIA",
        emisor: "adnia",
      };

      setHistorial((prev) => [...prev, respuestaIA]);
      registrarEnMemoria(respuestaIA);
    } catch (error) {
      const errorMsg = { texto: "❌ Error de conexión con ADNIA.", emisor: "sistema" };
      setHistorial((prev) => [...prev, errorMsg]);
      registrarEnMemoria(errorMsg);
    }
  };

  const manejarEnter = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      enviarMensaje();
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [historial]);

  useEffect(() => {
    if (usuarioInactivo && historial.length > 0) {
      const mensajeProactivo = {
        texto: "🧠 Parece que estás reflexionando. ¿Quieres que te proponga una acción jurídica?",
        emisor: "adnia",
      };
      setHistorial((prev) => [...prev, mensajeProactivo]);
      registrarEnMemoria(mensajeProactivo);
      setUsuarioInactivo(false);
    }
  }, [usuarioInactivo]);

  return (
    <div style={estilos.chatContainer}>
      <div style={estilos.chatBox}>
        {historial.map((msg, i) => (
          <div
            key={i}
            style={{
              ...estilos.mensaje,
              alignSelf:
                msg.emisor === "usuario"
                  ? "flex-end"
                  : msg.emisor === "adnia"
                  ? "flex-start"
                  : "center",
              backgroundColor:
                msg.emisor === "usuario"
                  ? "#1f3a5f"
                  : msg.emisor === "adnia"
                  ? "#162c43"
                  : "#444",
              color: "#eee",
            }}
          >
            {msg.texto}
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <textarea
        value={entrada}
        onChange={(e) => setEntrada(e.target.value)}
        onKeyDown={manejarEnter}
        placeholder="Escribe una consulta para ADNIA..."
        style={estilos.textarea}
      />
      <button onClick={enviarMensaje} style={estilos.boton}>
        Enviar
      </button>
    </div>
  );
}

const estilos = {
  chatContainer: {
    width: "100%",
    maxWidth: "1400px",
    margin: "0 auto",
    marginBottom: "30px",
    padding: "20px",
    backgroundColor: "#0e1625",
    borderRadius: "10px",
    boxShadow: "0 0 20px rgba(0,255,255,0.05)",
  },
  chatBox: {
    flexGrow: 1,
    minHeight: "250px",
    maxHeight: "100%",
    overflowY: "auto",
    padding: "10px",
    display: "flex",
    flexDirection: "column",
    gap: "10px",
    marginBottom: "10px",
  },
  mensaje: {
    maxWidth: "100%",
    padding: "20px",
    borderRadius: "12px",
    fontSize: "16px",
    lineHeight: "1.5",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
  },
  textarea: {
    width: "100%",
    height: "60px",
    backgroundColor: "#111827",
    color: "#00ffd9",
    border: "1px solid #00ffd9",
    borderRadius: "8px",
    fontSize: "16px",
    padding: "12px",
    marginBottom: "10px",
    resize: "none",
  },
  boton: {
    backgroundColor: "#00ffd9",
    color: "#000",
    padding: "10px 20px",
    border: "none",
    borderRadius: "8px",
    fontWeight: "bold",
    cursor: "pointer",
    alignSelf: "flex-end",
    boxShadow: "0 0 10px #00ffd9",
  },
};

export default PanelMemoria;
