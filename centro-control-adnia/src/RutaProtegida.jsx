import React from "react";
import { Navigate } from "react-router-dom";

/**
 * Protege rutas según login y rol.
 * 
 * @param {ReactNode} children - El componente hijo (vista protegida)
 * @param {string} rolRequerido - Rol necesario para acceder (opcional)
 */
function RutaProtegida({ children, rolRequerido = null }) {
  const usuario = localStorage.getItem("usuario");
  const rol = localStorage.getItem("rol");

  // No hay sesión activa
  if (!usuario || !rol) {
    console.warn("🔐 Usuario no autenticado. Redirigiendo al login.");
    return <Navigate to="/" replace />;
  }

  // Tiene sesión, pero no el rol requerido
  if (rolRequerido && rol !== rolRequerido) {
    console.warn(`🚫 Acceso denegado para rol "${rol}". Se requiere: "${rolRequerido}"`);
    return <Navigate to="/no-autorizado" replace />;
  }

  // Usuario autenticado y autorizado
  return children;
}

export default RutaProtegida;
