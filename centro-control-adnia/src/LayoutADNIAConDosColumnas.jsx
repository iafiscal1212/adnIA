import React from "react";
import PanelEstadisticas from "./PanelEstadisticas";
import PanelSubida from "./PanelSubida";
import VistaPreviaDocumento from "./VistaPreviaDocumento";
import PanelTareas from "./PanelTareas";
import PanelAlertas from "./PanelAlertas";

function LayoutADNIAConDosColumnas({ usuario, textoRespuesta, onAnalizar, onTextoProcesado }) {
  return (
    <div className="p-6 bg-slate-900 min-h-screen text-white">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Columna izquierda/doble */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          <PanelEstadisticas usuario={usuario} />
          <PanelSubida onTextoProcesado={onTextoProcesado} />
          <VistaPreviaDocumento texto={textoRespuesta} onAnalizar={onAnalizar} />
          <PanelTareas />
        </div>

        {/* Columna lateral derecha */}
        <div className="flex flex-col gap-4">
          <div className="bg-zinc-800 p-4 rounded border border-cyan-500">
            <h3 className="text-cyan-300 font-bold mb-2">📡 Vigilancia Normativa</h3>
            <p>Monitorizando contradicciones en AEAT, Seguridad Social y BOE...</p>
          </div>

          <div className="bg-zinc-800 p-4 rounded border border-cyan-500">
            <h3 className="text-cyan-300 font-bold mb-2">📚 Historial de Consultas</h3>
            <input type="text" placeholder="Buscar en el historial..." className="w-full p-2 mb-2 bg-zinc-700 text-white rounded" />
            <button className="bg-emerald-500 text-black font-bold px-4 py-2 rounded hover:bg-emerald-400 w-full">
              Exportar historial
            </button>
          </div>

          <div className="bg-zinc-800 p-4 rounded border border-orange-500">
            <h3 className="text-orange-400 font-bold mb-2">⚠️ Incoherencias Detectadas</h3>
            <p>🔸 A BOE 12/2024 contradict ex.art. 3.2 de la LC</p>
          </div>

          <PanelAlertas />
        </div>
      </div>
    </div>
  );
}

export default LayoutADNIAConDosColumnas;
