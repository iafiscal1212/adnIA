import { useEffect, useState } from "react";

function PanelAlertas() {
  const [alertas, setAlertas] = useState([]);

  useEffect(() => {
  fetch("http://localhost:3002/alertas") // corregido el puerto
    .then((res) => res.json())
    .then((data) => setAlertas(data))
    .catch((err) => console.error("Error cargando alertas:", err));
}, []);

  return (
    <div className="mt-10 bg-zinc-900 border-l-4 border-yellow-400 p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-bold mb-4 text-yellow-300">⚠️ Alertas Legales Detectadas</h2>
      {alertas.length === 0 ? (
        <p className="italic text-zinc-400">No se han detectado conflictos.</p>
      ) : (
        <ul className="space-y-4 text-sm">
          {alertas.map((a, i) => (
            <li key={i} className="bg-zinc-800 p-4 rounded border border-yellow-600">
              <p className="text-white font-semibold">📰 {a.titular}</p>
              {a.trampa && <p className="text-red-400">🔍 Trampa legal: {a.trampa}</p>}
              {a.constitucion && (
                <div>
                  <p className="text-emerald-400">📜 Conflicto constitucional:</p>
                  <p className="ml-4">Art. {a.constitucion.articulo} - {a.constitucion.titulo}</p>
                  <p className="ml-4 text-zinc-300">🧠 {a.constitucion.texto}</p>
                </div>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default PanelAlertas;
