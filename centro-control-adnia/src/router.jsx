// src/router.jsx
import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import NoAutorizado from "./NoAutorizado";
import PanelFiscal from "./PanelFiscal";
import PanelCivil from "./PanelCivil";
import PanelPenal from "./PanelPenal";
import PanelAdministrativo from "./PanelAdministrativo";
import PanelSocial from "./PanelSocial";
import PanelAdmin from "./PanelAdmin";
import PanelSelector from "./PanelSelector";
import PanelBlockchain from "./PanelBlockchain";

function RutaProtegida({ children, roles }) {
  const usuario = localStorage.getItem("usuario");
  const rol = localStorage.getItem("rol");

  if (!usuario) return <Navigate to="/" />;
  if (roles && !roles.includes(rol)) return <NoAutorizado />;

  return children;
}

function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<Login />} />
      <Route path="/no-autorizado" element={<NoAutorizado />} />
      <Route
        path="/selector"
        element={
          <RutaProtegida roles={["cliente", "asesoría", "admin"]}>
            <PanelSelector />
          </RutaProtegida>
        }
      />
      <Route
        path="/fiscal"
        element={
          <RutaProtegida roles={["cliente", "asesoría"]}>
            <PanelFiscal />
          </RutaProtegida>
        }
      />
      <Route
        path="/civil"
        element={
          <RutaProtegida roles={["cliente", "asesoría"]}>
            <PanelCivil />
          </RutaProtegida>
        }
      />
      <Route
        path="/penal"
        element={
          <RutaProtegida roles={["cliente", "asesoría"]}>
            <PanelPenal />
          </RutaProtegida>
        }
      />
      <Route
        path="/administrativo"
        element={
          <RutaProtegida roles={["cliente", "asesoría"]}>
            <PanelAdministrativo />
          </RutaProtegida>
        }
      />
      <Route
        path="/social"
        element={
          <RutaProtegida roles={["cliente", "asesoría"]}>
            <PanelSocial />
          </RutaProtegida>
        }
      />
      <Route
        path="/admin"
        element={
          <RutaProtegida roles={["admin"]}>
            <PanelAdmin />
          </RutaProtegida>
        }
      />
      <Route
        path="/blockchain"
        element={
          <RutaProtegida roles={["admin"]}>
            <PanelBlockchain />
          </RutaProtegida>
        }
      />
    </Routes>
  );
}

export default AppRouter;
