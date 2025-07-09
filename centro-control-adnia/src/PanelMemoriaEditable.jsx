import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

function PanelMemoriaEditable() {
  const [memoria, setMemoria] = useState([]);
  const [nuevo, setNuevo] = useState("");
  const [editando, setEditando] = useState(null);
  const navigate = useNavigate();

  // Protección de sesión ADNIA
  useEffect(() => {
    fetch("http://localhost:3002/dashboard", {
      method: "GET",
      credentials: "include"
    }).then(res => {
      if (res.status === 401) {
        localStorage.removeItem("usuario");
        localStorage.removeItem("rol");
        localStorage.removeItem("pais");
        navigate("/");
      }
    });
  }, [navigate]);

  // Cargar memoria al iniciar
  useEffect(() => {
    fetch("http://localhost:3002/memoria", { credentials: "include" })
      .then(res => res.json())
      .then(data => setMemoria(data || []));
  }, []);

  const guardarMemoria = (nuevaMemoria) => {
    setMemoria(nuevaMemoria);

    fetch("http://localhost:3002/memoria", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(nuevaMemoria)
    });
  };

  const eliminar = (index) => {
    const nueva = memoria.filter((_, i) => i !== index);
    guardarMemoria(nueva);
  };

  const actualizar = (index, valor) => {
    const nueva = [...memoria];
    nueva[index] = valor;
    guardarMemoria(nueva);
    setEditando(null);
  };

  const agregarNuevo = () => {
    if (nuevo.trim()) {
      const nueva = [...memoria, nuevo.trim()];
      guardarMemoria(nueva);
      setNuevo("");
    }
  };

  return (
    <div className="bg-zinc-950 text-green-400 font-mono p-6 border border-lime-500 rounded-xl shadow-xl max-w-3xl mx-auto">
      <h2 className="text-xl font-bold text-lime-300 mb-4">🧠 Edición de Memoria Estratégica</h2>
      <ul className="space-y-2 mb-6">
        {memoria.map((item, index) => (
          <li key={index} className="bg-zinc-800 p-3 rounded border border-lime-600">
            {editando === index ? (
              <div className="flex flex-col gap-2">
                <textarea
                  className="bg-black text-green-200 p-2 w-full"
                  value={item}
                  onChange={(e) => actualizar(index, e.target.value)}
                />
                <button
                  onClick={() => setEditando(null)}
                  className="bg-green-700 hover:bg-green-600 text-white px-2 py-1 rounded"
                >
                  Guardar
                </button>
              </div>
            ) : (
              <div className="flex justify-between items-start gap-2">
                <span>{item}</span>
                <div className="flex gap-1">
                  <button
                    onClick={() => setEditando(index)}
                    className="bg-yellow-600 hover:bg-yellow-500 text-black font-bold px-2 rounded"
                  >
                    ✏️
                  </button>
                  <button
                    onClick={() => eliminar(index)}
                    className="bg-red-700 hover:bg-red-600 text-white font-bold px-2 rounded"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            )}
          </li>
        ))}
      </ul>

      <div className="flex flex-col gap-2">
        <textarea
          value={nuevo}
          onChange={(e) => setNuevo(e.target.value)}
          placeholder="Añadir nuevo punto a la memoria..."
          className="bg-black text-green-300 p-2 rounded"
        />
        <button
          onClick={agregarNuevo}
          className="bg-lime-500 hover:bg-lime-400 text-black font-bold py-2 px-4 rounded"
        >
          ➕ Añadir
        </button>
      </div>
    </div>
  );
}

export default PanelMemoriaEditable;
