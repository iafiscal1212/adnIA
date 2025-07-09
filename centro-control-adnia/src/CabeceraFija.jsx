// CabeceraFija.jsx — cabecera superior con navegación de ADNIA
import React from "react";
import { NavLink, useNavigate } from "react-router-dom";

function CabeceraFija() {
  const navigate = useNavigate();

  const cerrarSesion = () => {
    localStorage.clear();
    navigate("/");
  };

  const enlace = (ruta, texto) => (
    <NavLink
      to={ruta}
      className={({ isActive }) =>
        `px-4 py-2 mx-1 rounded font-mono text-sm border ${
          isActive ? "bg-emerald-400 text-black" : "bg-zinc-800 text-emerald-300 border-emerald-500 hover:bg-emerald-700"
        }`
      }
    >
      {texto}
    </NavLink>
  );

  return (
    <header className="sticky top-0 z-50 bg-black border-b border-emerald-600 shadow-lg py-3 px-6 flex flex-wrap justify-between items-center">
      <h1 className="text-xl font-bold text-emerald-300 tracking-wide">🧬 ADNIA</h1>

      <nav className="flex flex-wrap gap-2 mt-2 sm:mt-0">
        {enlace("/dashboard", "Inicio")}
        {enlace("/fiscal", "Fiscal")}
        {enlace("/penal", "Penal")}
        {enlace("/civil", "Civil")}
        {enlace("/administrativo", "Administrativo")}
        {enlace("/social", "Social")}
      </nav>

      <button
        onClick={cerrarSesion}
        className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-500 ml-2"
      >
        Cerrar sesión
      </button>
    </header>
  );
}

export default CabeceraFija;
