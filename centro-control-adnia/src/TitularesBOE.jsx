import { useEffect, useState } from "react";

function TitularesBOE() {
  const [titulares, setTitulares] = useState([]);

  useEffect(() => {
    fetch("http://localhost:3002/boe", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => {
        if (data.length > 0) {
          setTitulares(data[data.length - 1].titulares);
        }
      });
  }, []);

  return (
    <div className="mt-10 bg-zinc-800 p-6 rounded-lg shadow-lg">
      <h2 className="text-xl font-semibold mb-4 text-emerald-400">📰 Últimos Titulares BOE</h2>
      {titulares.length === 0 ? (
        <p className="text-zinc-400 italic">Cargando titulares...</p>
      ) : (
        <ul className="list-disc list-inside space-y-1 text-sm">
          {titulares.map((t, i) => (
            <li key={i}>{t}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default TitularesBOE;
