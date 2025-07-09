
import React from "react";

function VistaPreviaDocumento({ texto, onAnalizar }) {
  return (
    <div className="bg-zinc-800 text-green-300 p-6 rounded-lg border border-emerald-500 mt-6">
      <h3 className="text-emerald-400 font-bold text-xl mb-4">📄 Vista Previa del Documento</h3>
      <div className="max-h-[400px] overflow-y-auto whitespace-pre-wrap text-base bg-zinc-900 p-4 rounded">
        {texto || "(Sin contenido extraído)"}
      </div>

      <button
        onClick={onAnalizar}
        className="mt-6 bg-lime-500 hover:bg-lime-400 text-black font-bold py-3 px-6 rounded"
      >
        🧠 Enviar a ADNIA para analizar
      </button>
    </div>
  );
}

export default VistaPreviaDocumento;
