// Navbar.jsx con estilo retro-glow y control por rol

import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

function Navbar() {
  const usuario = localStorage.getItem("usuario");
  const rol = localStorage.getItem("rol");
  const navigate = useNavigate();

  const cerrarSesion = () => {
    localStorage.clear();
    navigate("/");
  };

  const enlace = (ruta, texto) => (
    <NavLink
      to={ruta}
      className={({ isActive }) =>
        `px-4 py-2 mx-2 font-mono text-sm rounded transition-all duration-200 shadow-md
         ${isActive ? "bg-emerald-400 text-black" : "bg-zinc-900 text-green-300 hover:bg-emerald-700"}`
      }
    >
      {texto}
    </NavLink>
  );

  return (
    <nav className="bg-zinc-950 p-4 border-b border-emerald-500 flex flex-wrap justify-between items-center">
      <div className="text-2xl font-bold text-emerald-400 font-mono">🔷 ADNIA</div>

      <div className="flex flex-wrap items-center mt-2 sm:mt-0">
        {rol === "admin" && enlace("/dashboard", "Dashboard")}
        {(rol === "admin" || rol === "asesoria") && enlace("/fiscal", "Fiscal")}
        {/* Agrega más módulos aquí según el rol */}
        {usuario && (
          <button
            onClick={cerrarSesion}
            className="ml-4 bg-red-600 text-white font-bold px-3 py-1 rounded hover:bg-red-500"
          >
            Cerrar sesión
          </button>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
