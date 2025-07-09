
import React, { useState } from "react";

function PanelEspia() {
  const [sospecha, setSospecha] = useState("");
  const [resultado, setResultado] = useState("");
  const [cargando, setCargando] = useState(false);

  const lanzarEspia = async () => {
    if (!sospecha.trim()) return;
    setCargando(true);
    try {
      const res = await fetch("http://localhost:3002/resolver", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          pregunta: `Agente Espía Jurídico: analiza a fondo esta sospecha legal. Busca contradicciones normativas, estimaciones abusivas o anomalías ocultas. Si hay trampa, dilo: \"Aquí hay trampa, jefa.\"\n\nSospecha: ${sospecha}`,
          categoria: "espia",
        credentials: "include"
        })
      });
      const data = await res.json();
      setResultado(data.respuesta || "(Sin respuesta de ADNIA)");
    } catch (err) {
      setResultado(`⚠️ Error al contactar con el espía: ${err.message}`);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="card max-w-4xl mx-auto text-cyan-200">
      <h2 className="text-2xl font-bold mb-4 text-pink-400">🕶️ Fiscalista ADNIA — Unidad Espía</h2>
      <textarea
        value={sospecha}
        onChange={(e) => setSospecha(e.target.value)}
        placeholder="Escribe aquí la sospecha legal, fiscal o constitucional..."
        rows={6}
      />
      <button
        onClick={lanzarEspia}
        disabled={cargando}
        className="mt-4 bg-pink-500 hover:bg-pink-400 text-black"
      >
        {cargando ? "Infiltrando..." : "🧠 Infiltrar Sospecha"}
      </button>

      {resultado && (
        <div className="mt-6 p-4 bg-zinc-900 border border-pink-500 rounded">
          <h4 className="text-pink-300 font-bold mb-2">📢 Informe de Inteligencia:</h4>
          <p>{resultado}</p>
        </div>
      )}
    </div>
  );
}

export default PanelEspia;
