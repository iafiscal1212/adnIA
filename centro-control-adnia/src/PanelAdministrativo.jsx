import React, { useState, useContext, useEffect } from "react";
import VistaPreviaDocumento from "./VistaPreviaDocumento";
import { ADNIAContext } from "./ADNIAContext";
import { useNavigate } from "react-router-dom";

function PanelSubida() {
  const [archivo, setArchivo] = useState(null);
  const [mensaje, setMensaje] = useState("");
  const [texto, setTexto] = useState("");
  const [respuesta, setRespuesta] = useState("");
  const {
    usuario, rol, pais,
    moduloActual, memoriaCorta, memoriaLarga, setDocumentoTexto, sugerencia
  } = useContext(ADNIAContext);
  const navigate = useNavigate();

  // 🔒 Protección ADNIA: si se pierde sesión, te echa a login
  useEffect(() => {
    fetch("http://localhost:3002/dashboard", {
      method: "GET",
      credentials: "include"
    }).then(res => {
      if (res.status === 401) {
        localStorage.removeItem("usuario");
        localStorage.removeItem("rol");
        localStorage.removeItem("pais");
        // Si tienes setters de contexto, puedes resetear aquí también
        navigate("/");
      }
    });
  }, [navigate]);

  const manejarSubida = async () => {
    if (!archivo) return;
    const formData = new FormData();
    formData.append("documento", archivo);

    try {
      const res = await fetch("http://localhost:3002/api/analizar", {
        method: "POST",
        body: formData,
        credentials: "include"
      });

      const data = await res.json();
      if (data.resultado) {
        setTexto(data.resultado);
        setMensaje("✅ Documento procesado correctamente");
        setDocumentoTexto(data.resultado);
      } else {
        setMensaje("⚠️ No se pudo extraer texto del documento");
      }
    } catch (err) {
      setMensaje(`❌ Error al subir archivo: ${err.message}`);
    }
  };

  // El análisis manda TODO el contexto estratégico
  const enviarADNIA = async () => {
    try {
      const textoRecortado = texto.slice(0, 3000);

      const res = await fetch("http://localhost:3002/resolver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
        credentials: "include", // SIEMPRE
          usuario,
          rol,
          pais,
          modulo: moduloActual,
          historial: memoriaCorta,
          memoriaLarga,
          sugerencia,
          documentoTexto: textoRecortado,
          pregunta: `Este es un documento legal. Por favor, resume su contenido, extrae las frases clave y presenta un análisis jurídico:\n\n${textoRecortado}`,
        }),
      });

      const data = await res.json();
      setRespuesta(data.respuesta || "(Sin respuesta de ADNIA)");
    } catch (err) {
      setRespuesta(`❌ Error en ADNIA: ${err.message}`);
    }
  };

  return (
    <div
      id="panel-subida"
      style={{
        marginTop: "30px",
        paddingBottom: "60px",
        color: "#00ffd9",
        fontFamily: "monospace",
        width: "100%",
        maxWidth: "1400px",
        marginLeft: "auto",
        marginRight: "auto",
      }}
    >
      <h2 style={{ fontSize: "1.5rem", fontWeight: "bold", marginBottom: "16px" }}>
        📂 Subida y Análisis de Documento
      </h2>

      <input
        type="file"
        accept=".pdf,.docx,.txt,.xml,.png,.jpg,.jpeg"
        onChange={(e) => setArchivo(e.target.files[0])}
        style={{
          width: "100%",
          maxWidth: "600px",
          padding: "10px",
          borderRadius: "8px",
          backgroundColor: "#111827",
          color: "#00ffd9",
          border: "1px solid #00ffd9",
          marginBottom: "20px",
        }}
      />

      <button
        onClick={manejarSubida}
        disabled={!archivo}
        style={{
          fontWeight: "bold",
          padding: "10px 20px",
          borderRadius: "8px",
          backgroundColor: archivo ? "#00ffd9" : "#1f3a5f",
          color: archivo ? "#000" : "#888",
          cursor: archivo ? "pointer" : "not-allowed",
          marginBottom: "20px",
        }}
      >
        Analizar Documento
      </button>

      {mensaje && <p className="mt-3 text-sm">{mensaje}</p>}

      {texto && (
        <div id="vista-documento">
          <VistaPreviaDocumento texto={texto} onAnalizar={enviarADNIA} />
        </div>
      )}

      {respuesta && (
        <div
          style={{
            marginTop: "40px",
            backgroundColor: "#0d1b2a",
            padding: "20px",
            borderRadius: "10px",
            border: "1px solid #00ffd9",
          }}
        >
          <h4 style={{ color: "#66ff99", fontWeight: "bold", marginBottom: "10px" }}>
            📢 Respuesta de ADNIA:
          </h4>
          <p>{respuesta}</p>

          <button
            onClick={() => window.print()}
            style={{
              marginTop: "20px",
              backgroundColor: "#66ff99",
              color: "#000",
              fontWeight: "bold",
              padding: "10px 20px",
              borderRadius: "8px",
              cursor: "pointer",
            }}
          >
            📤 Exportar análisis a PDF
          </button>
        </div>
      )}
    </div>
  );
}

export default PanelSubida;
