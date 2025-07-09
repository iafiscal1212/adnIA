import React, { useEffect, useState } from "react";
import ParticlesBackground from "./ParticlesBackground"; // 👈 nuevo

const SplashScreen = () => {
  const [visibleLines, setVisibleLines] = useState(0);

  const lines = [
    "Inicializando sistema ADNIA [v.1.0.0-local]...",
    "Cargando módulo de percepción cuántica...",
    "Conectando a matriz de inteligencia fiscal, contable, mercantil...",
    "Sincronizando nodos de vigilancia normativa [AEAT, Seguridad Social, CNMV] ✔",
    "Activando retina legal... 🧠⚡",
    "» ADNIA ONLINE — Aquí no obedecemos a la ignorancia disfrazada de ley."
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setVisibleLines((prev) => {
        if (prev < lines.length) return prev + 1;
        clearInterval(interval);
        return prev;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{
      backgroundColor: "black",
      color: "#00ff88",
      fontFamily: "'Share Tech Mono', monospace",
      fontSize: "1rem",
      height: "100vh",
      padding: "2rem",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      position: "relative",
      zIndex: 0
    }}>
      <ParticlesBackground />
      <div style={{ position: "relative", zIndex: 1 }}>
        {lines.slice(0, visibleLines).map((line, i) => (
          <p key={i} style={{ marginBottom: "0.5rem", whiteSpace: "pre-wrap" }}>
            {line}
          </p>
        ))}
      </div>
    </div>
  )};

export default SplashScreen;
