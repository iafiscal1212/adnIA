import React, { createContext, useState, useContext } from "react";

const UsuarioContext = createContext();

export function useUsuario() {
  return useContext(UsuarioContext);
}

export function UsuarioProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [rol, setRol] = useState(null);

  return (
    <UsuarioContext.Provider value={{ usuario, setUsuario, rol, setRol }}>
      {children}
    </UsuarioContext.Provider>
  );
}
