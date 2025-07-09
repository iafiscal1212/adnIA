import React, { useState } from "react";

function PanelTareas({ onTareaLanzada }) {
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [respuesta, setRespuesta] = useState("");

  const lanzarTarea = async () => {
    if (!titulo.trim() || !descripcion.trim()) return;

    const prompt = `Agente Fiscalista ADNIA. Tarea: ${titulo}. Instrucciones: ${descripcion}. Analiza la ley aplicable, detecta contradicciones o abusos legales y sugiere acciones legales posibles.`;

    try {
      const res = await fetch("http://localhost:3002/resolver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta: prompt, categoria: "fiscal" })      ,
        credentials: "include"
      });

      const data = await res.json();
      setRespuesta(data.respuesta || "(Sin respuesta de ADNIA)");
      if (onTareaLanzada) onTareaLanzada({ titulo, descripcion, respuesta: data.respuesta });
    } catch (err) {
      setRespuesta("⚠️ Error al contactar con el motor jurídico interno.");
    }
  };

  return (
    <div className="card">
      <h2>🎯 Crear Tarea Jurídica ADNIA</h2>

      <input
        type="text"
        placeholder="Título de la tarea (ej. Revisar notificación AEAT)"
        value={titulo}
        onChange={(e) => setTitulo(e.target.value)}
        className="mb-2"
      />

      <textarea
        rows="4"
        placeholder="Describe la tarea con detalle..."
        value={descripcion}
        onChange={(e) => setDescripcion(e.target.value)}
        className="w-full p-2 bg-zinc-900 text-green-300 border border-emerald-500 rounded"
      />

      <button onClick={lanzarTarea} className="mt-3 bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-4 py-2 rounded">
        🚀 Lanzar Tarea
      </button>

      {respuesta && (
        <div className="respuesta mt-4">
          <h4 className="text-lime-400 font-bold mb-2">🧠 Respuesta del Agente:</h4>
          <p>{respuesta}</p>
        </div>
      )}
    </div>
  );
}

export default PanelTareas;
