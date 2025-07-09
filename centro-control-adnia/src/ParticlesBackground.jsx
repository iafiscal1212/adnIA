// src/ParticlesBackground.jsx
import React from "react";
import Particles from "react-tsparticles";
import { loadFull } from "tsparticles";

const ParticlesBackground = () => {
  const particlesInit = async (main) => {
    await loadFull(main);
  };

  return (
    <Particles
      id="tsparticles"
      init={particlesInit}
      options={{
        fullScreen: { enable: true, zIndex: -1 },
        background: { color: "#000000" },
        particles: {
          color: { value: "#00ff88" },
          number: { value: 50 },
          size: { value: 2 },
          move: {
            enable: true,
            speed: 0.3,
            direction: "none",
            outModes: { default: "bounce" }
          },
          links: {
            enable: true,
            color: "#00ff88",
            distance: 90,
            opacity: 0.25
          }
        },
        interactivity: {
          events: { onHover: { enable: true, mode: "repulse" } },
          modes: { repulse: { distance: 80 } }
        }
      }}
    />
  );
};

export default ParticlesBackground;
