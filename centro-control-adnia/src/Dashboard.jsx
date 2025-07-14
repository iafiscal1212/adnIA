// Dashboard.jsx
import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Particles from "react-tsparticles";

const modulos = [
  { nombre: "Fiscal", path: "/fiscal", icon: "💼" },
  { nombre: "Penal", path: "/penal", icon: "⚖️" },
  { nombre: "Civil", path: "/civil", icon: "📜" },
  { nombre: "Social", path: "/social", icon: "🤝" },
  { nombre: "Administrativo", path: "/administrativo", icon: "🏛️" },
  { nombre: "Admin", path: "/admin", icon: "👤" }
];

const fraseADNIA = '“Aquí no obedecemos a la ignorancia disfrazada de ley...”';

import ChatInterface from "./ChatInterface";

function Dashboard({ onLogout }) {
  const navigate = useNavigate();
  const [frase, setFrase] = useState("");
  const fraseRef = useRef(null);
  const [activeChat, setActiveChat] = useState(null); // Estado para controlar la vista de chat

  // Efecto typing en la frase
  useEffect(() => {
    let i = 0;
    setFrase("");
    const interval = setInterval(() => {
      setFrase(fraseADNIA.slice(0, i));
      i++;
      if (i > fraseADNIA.length) clearInterval(interval);
    }, 22);
    return () => clearInterval(interval);
  }, []);

  // Efecto fade-in entrada
  useEffect(() => {
    document.body.style.background = "#222933";
    return () => { document.body.style.background = ""; };
  }, []);

  return (
    <div style={{ minHeight: "100vh", width: "100vw", overflowX: "hidden", position: "relative" }}>
      {/* Fondo partículas */}
      <Particles
        id="tsparticles"
        options={{
          background: { color: { value: "#222933" } },
          fpsLimit: 60,
          interactivity: { detectsOn: "canvas", events: { resize: true } },
          particles: {
            color: { value: "#00ffd9" },
            links: { enable: true, color: "#00ffd9", opacity: 0.12, distance: 160 },
            move: { enable: true, speed: 0.7 },
            opacity: { value: 0.17 },
            size: { value: { min: 1, max: 2.6 } },
            number: { value: 66 }
          }
        }}
        style={{
          position: "absolute",
          top: 0, left: 0,
          width: "100vw",
          height: "100vh",
          zIndex: 0
        }}
      />
      <div
        style={{
          position: "relative",
          zIndex: 2,
          minHeight: "100vh",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          paddingTop: "40px"
        }}
        className="fade-in-adnia"
      >
        {/* Título */}
        <h1 style={{
          color: "#00ffd9",
          fontWeight: 900,
          fontSize: "3.3rem",
          textShadow: "0 0 38px #00ffd9, 0 0 8px #00ffd9aa",
          letterSpacing: "1px",
          marginBottom: "0.1em"
        }}>
          Panel Central ADNIA
        </h1>

        {/* Frase con efecto typing */}
        <div style={{
          color: "#fff",
          fontStyle: "italic",
          fontSize: "1.45rem",
          margin: "10px 0 30px 0",
          minHeight: "2.5rem",
          textAlign: "center",
          textShadow: "0 0 15px #00ffd9cc"
        }}>
          <span ref={fraseRef}>{frase}</span>
          <span className="typing-cursor" style={{ color: "#00ffd9" }}>|</span>
        </div>

        {/* Módulos o Interfaz de Chat */}
        {activeChat ? (
          <ChatInterface initialJurisdiction={activeChat} onBack={() => setActiveChat(null)} />
        ) : (
          <div className="adnia-modules-grid">
            {modulos.map(mod =>
              <div
                key={mod.nombre}
                className="adnia-module-card"
                tabIndex={0}
                style={{ outline: "none", cursor: 'pointer' }}
                onClick={() => setActiveChat(mod.nombre)}
              >
                <span className="adnia-module-icon">{mod.icon}</span>
                <span className="adnia-module-label">{mod.nombre}</span>
              </div>
            )}
          </div>
        )}

        {/* Botón cerrar sesión */}
        <button
          onClick={onLogout}
          className="adnia-logout-btn"
        >
          Cerrar sesión
        </button>
      </div>

      {/* Estilos CSS en JS */}
      <style>{`
        .fade-in-adnia {
          animation: fadeInAdnia 1.2s cubic-bezier(.77,.1,.58,1.0) both;
        }
        @keyframes fadeInAdnia {
          0% { opacity: 0; transform: translateY(40px);}
          100% { opacity: 1; transform: none; }
        }

        .typing-cursor {
          animation: blinkAdnia 1.15s steps(2, start) infinite;
        }
        @keyframes blinkAdnia {
          0%,100% { opacity: 1; }
          50% { opacity: 0; }
        }

        .adnia-modules-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 36px 50px;
          width: 90vw;
          max-width: 980px;
          justify-items: center;
          align-items: center;
          margin: 24px 0 38px 0;
        }

        .adnia-module-card {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-width: 210px;
          min-height: 120px;
          background: #141b23;
          border-radius: 22px;
          box-shadow: 0 0 32px #00ffd9b4;
          transition: box-shadow 0.18s, transform 0.18s;
          text-decoration: none;
          color: #00ffd9;
          font-size: 1.21rem;
          font-weight: bold;
          outline: none;
          border: none;
          position: relative;
          will-change: transform, box-shadow;
        }
        .adnia-module-card:hover, .adnia-module-card:focus {
          box-shadow: 0 0 54px #00ffd9cc, 0 0 24px #fff6;
          transform: scale(1.08) rotate(-1.5deg);
          z-index: 3;
        }

        .adnia-module-icon {
          font-size: 2.7rem;
          margin-bottom: 0.5rem;
          transition: filter 0.23s, transform 0.23s;
          filter: drop-shadow(0 0 7px #00ffd9cc);
        }
        .adnia-module-card:hover .adnia-module-icon,
        .adnia-module-card:focus .adnia-module-icon {
          filter: drop-shadow(0 0 18px #00ffd9ff);
          transform: rotate(-5deg) scale(1.15);
        }
        .adnia-module-label {
          color: #00ffd9;
          font-size: 1.13em;
          margin-top: 0.25em;
        }

        .adnia-logout-btn {
          margin-top: 40px;
          background: #ff5252;
          color: #fff;
          border: none;
          font-weight: bold;
          font-size: 1.3rem;
          border-radius: 16px;
          padding: 18px 48px;
          cursor: pointer;
          box-shadow: 0 0 28px #ff525288;
          transition: background 0.2s, box-shadow 0.2s, transform 0.18s;
        }
        .adnia-logout-btn:hover, .adnia-logout-btn:focus {
          background: #ff2929;
          box-shadow: 0 0 48px #ff5252cc, 0 0 8px #fff4;
          transform: scale(1.06);
        }

        @media (max-width: 900px) {
          .adnia-modules-grid {
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 30px 16px;
            max-width: 98vw;
          }
          .adnia-module-card {
            min-width: 145px;
            min-height: 90px;
          }
        }
        @media (max-width: 600px) {
          .fade-in-adnia { padding-top: 16px !important; }
          .adnia-modules-grid { gap: 18px 6px; }
          .adnia-module-card {
            min-width: 115px;
            min-height: 70px;
            font-size: 1rem;
          }
          .adnia-module-icon { font-size: 2rem; }
          .adnia-logout-btn {
            padding: 10px 22px;
            font-size: 1rem;
          }
        }
      `}</style>
    </div>
  );
}

export default Dashboard;
