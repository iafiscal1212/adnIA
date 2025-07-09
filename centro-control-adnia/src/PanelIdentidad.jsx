// PanelIdentidad.jsx
import { useEffect, useState } from "react";

function PanelIdentidad() {
  const [manifiesto, setManifiesto] = useState("");

  useEffect(() => {
    fetch("/manifesto.md")
      .then((res) => res.text())
      .then((data) => setManifiesto(data));
  }, []);

  return (
    <div className="bg-black text-green-400 font-mono p-6 border border-cyan-400 rounded-xl shadow-xl max-h-[500px] overflow-y-auto">
      <h2 className="text-xl font-bold text-cyan-300 mb-4">🧬 Núcleo de Identidad ADNIA</h2>
      <pre className="whitespace-pre-wrap text-sm leading-relaxed">
        {manifiesto}
      </pre>
    </div>
  );
}

export default PanelIdentidad;
