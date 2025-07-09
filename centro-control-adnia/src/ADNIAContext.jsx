import React, { createContext, useState, useEffect } from "react";
import { BACKEND_URL } from "./config";

// Persistencia local para memoria larga (puedes dejarlo igual)
const getLongMemory = () => {
  try {
    const mem = localStorage.getItem("adnia_memoria_larga");
    return mem ? JSON.parse(mem) : [];
  } catch {
    return [];
  }
};
const saveLongMemory = (arr) => {
  localStorage.setItem("adnia_memoria_larga", JSON.stringify(arr));
};

export const ADNIAContext = createContext();

export const ADNIAProvider = ({ children }) => {
  const [usuario, setUsuario] = useState("");
  const [rol, setRol] = useState("cliente");
  const [pais, setPais] = useState("España");
  const [memoriaCorta, setMemoriaCorta] = useState([]);
  const [memoriaLarga, setMemoriaLarga] = useState(getLongMemory());
  const [documentoTexto, setDocumentoTexto] = useState("");
  const [sugerencia, setSugerencia] = useState("");
  const [historial, setHistorial] = useState([]);
  const [moduloActual, setModuloActual] = useState("Fiscal");
  const [favoritos, setFavoritos] = useState([]);
  const [modelo, setModelo] = useState("mistral-large-latest");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Valida con backend la sesión al montar
    const checkSession = async () => {
      try {
        const res = await fetch(`${BACKEND_URL}/session`, { credentials: "include" });
        const data = await res.json();
        if (data.ok) {
          setUsuario(data.usuario);
          setRol(data.rol || "cliente");
          setPais(data.pais || "España");
        } else {
          setUsuario("");
          setRol("cliente");
          setPais("España");
          localStorage.removeItem("usuario");
          localStorage.removeItem("rol");
          localStorage.removeItem("pais");
        }
      } catch {
        setUsuario("");
        setRol("cliente");
        setPais("España");
        localStorage.removeItem("usuario");
        localStorage.removeItem("rol");
        localStorage.removeItem("pais");
      }
      setLoading(false);
    };
    checkSession();
  }, []);

  // Login desde el frontend tras login correcto
  const login = (data) => {
    setUsuario(data.usuario);
    setRol(data.rol || "cliente");
    setPais(data.pais || "España");
    localStorage.setItem("usuario", data.usuario);
    localStorage.setItem("rol", data.rol || "cliente");
    localStorage.setItem("pais", data.pais || "España");
  };

  // Logout mejorado: limpia sesión y almacenamiento local
  const logout = () => {
    setUsuario("");
    setRol("cliente");
    setPais("España");
    localStorage.removeItem("usuario");
    localStorage.removeItem("rol");
    localStorage.removeItem("pais");
    // Si tienes endpoint de logout en backend, puedes añadir aquí:
    // fetch(`${BACKEND_URL}/logout`, { method: "POST", credentials: "include" });
  };

  // Gestión de memorias
  const guardarEnMemoriaLarga = (dato) => {
    const nueva = [...memoriaLarga, dato];
    setMemoriaLarga(nueva);
    saveLongMemory(nueva);
  };

  const resetMemorias = () => {
    setMemoriaCorta([]);
    setMemoriaLarga([]);
    localStorage.removeItem("adnia_memoria_larga");
  };

  return (
    <ADNIAContext.Provider value={{
      usuario, setUsuario,
      rol, setRol,
      pais, setPais,
      memoriaCorta, setMemoriaCorta,
      memoriaLarga, setMemoriaLarga,
      documentoTexto, setDocumentoTexto,
      sugerencia, setSugerencia,
      historial, setHistorial,
      moduloActual, setModuloActual,
      guardarEnMemoriaLarga, resetMemorias,
      favoritos, setFavoritos,
      modelo, setModelo,
      loading,
      login,
      logout
    }}>
      {children}
    </ADNIAContext.Provider>
  );
};
