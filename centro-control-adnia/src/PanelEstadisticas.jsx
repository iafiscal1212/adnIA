// ✅ PanelEstadisticas.jsx corregido

import React, { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

function PanelEstadisticas({ usuario }) {
  const [datos, setDatos] = useState([]);

  useEffect(() => {
    if (!usuario) return;

  fetch(`http://localhost:3002/conversaciones_${usuario}.json`, { credentials: "include" })
  .then(res => res.json())
  .then(conversaciones => {
    const conteo = {};
    conversaciones.forEach(c => {
      const cat = c.categoria || "sin_categoria";
      conteo[cat] = (conteo[cat] || 0) + 1;
    });
    const formateado = Object.entries(conteo).map(([categoria, total]) => ({ categoria, total }));
    setDatos(formateado);
  });
  }, [usuario]);

  return (
    <div className="panel-estadisticas bg-zinc-950 text-green-400 font-mono p-6 border border-cyan-500 rounded-xl shadow-xl max-w-4xl mx-auto">
      <h2 className="text-xl font-bold text-cyan-300 mb-4">📊 Estadísticas Jurídicas por Categoría</h2>
      {datos.length === 0 ? (
        <p className="italic text-zinc-400">No hay suficientes datos para mostrar.</p>
      ) : (
        <>
          <button
            onClick={() => window.print()}
            className="bg-cyan-500 hover:bg-cyan-400 text-black font-bold px-4 py-2 rounded mb-4"
          >
            📊 Exportar estadísticas a PDF
          </button>

          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={datos} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="categoria" stroke="#00ffe7" />
              <YAxis stroke="#00ffe7" />
              <Tooltip wrapperStyle={{ fontFamily: 'monospace' }} />
              <Legend />
              <Bar dataKey="total" fill="#00ff88" />
            </BarChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
}

export default PanelEstadisticas;
