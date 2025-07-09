import React, { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import Particles from "react-tsparticles";

const fraseADNIA = "Aquí no obedecemos a la ignorancia disfrazada de ley...";

function BienvenidaADNIA() {
  const navigate = useNavigate();
  const [frase, setFrase] = useState("");
  const fraseRef = useRef(null);

  // Efecto typing en la frase
  useEffect(() => {
    let i = 0;
    setFrase("");
    const interval = setInterval(() => {
      setFrase(fraseADNIA.slice(0, i));
      i++;
      if (i > fraseADNIA.length) clearInterval(interval);
    }, 26);
    return () => clearInterval(interval);
  }, []);

  // Efecto fade-in entrada
  useEffect(() => {
    document.body.style.background = "#061727";
    return () => { document.body.style.background = ""; };
  }, []);

  return (
    <div style={{
      minHeight: "100vh",
      width: "100vw",
      overflow: "hidden",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      position: "relative"
    }}>
      {/* Fondo partículas */}
      <Particles
        id="tsparticles-welcome"
        options={{
          background: { color: { value: "#061727" } },
          fpsLimit: 60,
          interactivity: { detectsOn: "canvas", events: { resize: true } },
          particles: {
            color: { value: "#00ffd9" },
            links: { enable: true, color: "#00ffd9", opacity: 0.14, distance: 170 },
            move: { enable: true, speed: 0.75 },
            opacity: { value: 0.16 },
            size: { value: { min: 1, max: 2.8 } },
            number: { value: 55 }
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
          zIndex: 2,
          width: "100vw",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "30px 8vw"
        }}
        className="fade-in-adnia"
      >
        <h1 style={{
          fontSize: "3.1rem",
          fontWeight: 900,
          textShadow: "0 0 36px #00ffd9, 0 0 7px #fff",
          color: "#00ffd9",
          marginBottom: "22px",
          letterSpacing: "1.5px"
        }}>
          ADNIA está despertando...
        </h1>
        <div style={{
          fontSize: "1.67rem",
          color: "#fff",
          textShadow: "0 0 12px #00ffd9",
          minHeight: "2.5rem",
          textAlign: "center",
          fontStyle: "italic",
          marginBottom: "40px",
          letterSpacing: "0.6px"
        }}>
          <span ref={fraseRef}>{frase}</span>
          <span className="typing-cursor" style={{ color: "#00ffd9" }}>|</span>
        </div>
        <button
          onClick={() => navigate("/")}
          className="adnia-welcome-btn"
        >
          Entrar al panel ADNIA
        </button>
      </div>
      <style>{`
        .fade-in-adnia {
          animation: fadeInAdnia 1.3s cubic-bezier(.77,.1,.58,1.0) both;
        }
        @keyframes fadeInAdnia {
          0% { opacity: 0; transform: translateY(40px);}
          100% { opacity: 1; transform: none; }
        }
        .typing-cursor {
          animation: blinkAdnia 1.09s steps(2, start) infinite;
        }
        @keyframes blinkAdnia {
          0%,100% { opacity: 1; }
          50% { opacity: 0; }
        }
        .adnia-welcome-btn {
          background: #00ffd9;
          color: #000;
          font-weight: bold;
          font-size: 1.35rem;
          border: none;
          border-radius: 13px;
          padding: 18px 56px;
          cursor: pointer;
          margin-top: 6px;
          box-shadow: 0 0 23px #00ffd9cc;
          transition: background 0.18s, box-shadow 0.18s, transform 0.18s;
        }
        .adnia-welcome-btn:hover, .adnia-welcome-btn:focus {
          background: #00d1a6;
          box-shadow: 0 0 40px #00ffd9ee, 0 0 7px #fff7;
          transform: scale(1.06);
        }
        @media (max-width: 600px) {
          h1 { font-size: 2.2rem !important; }
          .adnia-welcome-btn { font-size: 1.1rem; padding: 10px 26px; }
          div[style*="font-size: 1.67rem"] { font-size: 1.12rem !important; }
        }
      `}</style>
    </div>
  );
}

export default BienvenidaADNIA;
