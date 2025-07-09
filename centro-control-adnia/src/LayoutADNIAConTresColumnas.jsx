import React from "react";
import PanelFiscal from "./PanelFiscal";
import PanelCivil from "./PanelCivil";
import PanelPenal from "./PanelPenal";

function LayoutADNIAConTresColumnas() {
  return (
    <div className="p-6 bg-slate-900 min-h-screen text-white">
      <div className="flex flex-col lg:flex-row gap-6 justify-center">
        <div className="w-full max-w-md">
          <PanelFiscal />
        </div>
        <div className="w-full max-w-md">
          <PanelCivil />
        </div>
        <div className="w-full max-w-md">
          <PanelPenal />
        </div>
      </div>

      <footer className="mt-10 text-center text-sm text-gray-400">
        <p>© 2025 ADNIA IA Jurídica</p>
      </footer>
    </div>
  );
}

export default LayoutADNIAConTresColumnas;
