// ✅ src/Vigilancia.jsx — ADNIA en modo vigilancia pasiva y activa
import React, { useEffect, useState } from 'react';

const Vigilancia = () => {
  const [alertas, setAlertas] = useState([]);
  const [nuevas, setNuevas] = useState([]);

  useEffect(() => {
    const fetchAlertas = async () => {
      try {
        const res = await fetch("http://localhost:3002/alertas", { credentials: "include" });
        const data = await res.json();

        // Comparamos con alertas anteriores (simplemente por longitud)
        if (data.length > alertas.length) {
          const nuevasAlertas = data.slice(alertas.length);
          setNuevas(nuevasAlertas);
        }

        setAlertas(data);
      } catch (err) {
        console.error("Error al obtener alertas:", err);
      }
    };

    fetchAlertas();
    const interval = setInterval(fetchAlertas, 15000); // cada 15s
    return () => clearInterval(interval);
  }, [alertas]);

  return (
    <div style={{
      backgroundColor: "#000",
      color: "#00ff88",
      fontFamily: "'Share Tech Mono', monospace",
      height: "100vh",
      padding: "2rem",
      overflowY: "auto"
    }}>
      <h2 style={{ color: "#00ffe7", fontSize: "1.5rem", marginBottom: "1rem" }}>
        🔍 Vigilancia Normativa — ADNIA Online
      </h2>

      {nuevas.length > 0 && (
        <div style={{ color: "#ff5555", marginBottom: "1rem" }}>
          ⚠️ Nuevas contradicciones detectadas:
          <ul>
            {nuevas.map((a, i) => (
              <li key={i} style={{ marginTop: "0.5rem" }}>
                {a.titular || a.trampa || "Conflicto registrado."}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <h3 style={{ color: "#00ffe7", marginTop: "1.5rem" }}>📚 Historial completo</h3>
        <ul style={{ listStyle: "square", paddingLeft: "1.5rem" }}>
          {alertas.map((a, i) => (
            <li key={i} style={{ marginTop: "0.4rem" }}>
              {a.titular || a.trampa || "Conflicto registrado."}
              {a.constitucion && (
                <div style={{ marginTop: "0.3rem", color: "#00ffaa" }}>
                  🧠 Art. {a.constitucion.articulo} CE — {a.constitucion.titulo}
                  <br />{a.constitucion.texto}
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default Vigilancia;


// ✅ En tu App.jsx añade esto para ruta oculta (usando React Router)
/*
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Vigilancia from './Vigilancia';

...
<Router>
  <Routes>
    <Route path="/" element={<SplashScreen />} />
    <Route path="/vigilancia" element={<Vigilancia />} />
  </Routes>
</Router>
*/
