import React, { useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./Login";
import Dashboard from "./Dashboard";
import BienvenidaADNIA from "./BienvenidaADNIA";
import { ADNIAContext } from "./ADNIAContext";
import PanelFiscal from "./PanelFiscal";
import PanelPenal from "./PanelPenal";
import PanelCivil from "./PanelCivil";
import PanelSocial from "./PanelSocial";
import PanelAdministrativo from "./PanelAdministrativo";
import PanelAdmin from "./PanelAdmin";
import PanelSubida from "./PanelSubida";
import PanelMemoria from "./PanelMemoria";
import PanelMemoriaEditable from "./PanelMemoriaEditable";
import PanelEspia from "./PanelEspia";
import PanelBlockchain from "./PanelBlockchain";
import PanelFavoritos from "./PanelFavoritos";
import PanelAlertas from "./PanelAlertas";
import PanelAuditoria from "./PanelAuditoria";

function ProtectedRoute({ children }) {
  const { usuario, loading } = useContext(ADNIAContext);
  if (loading) return <div>Cargando...</div>;
  return usuario ? children : <Navigate to="/" />;
}

function MainApp() {
  const { usuario, rol, login, loading } = useContext(ADNIAContext);

  // Esta función se pasa al Login y se invoca tras un login correcto
  const handleLogin = (data) => {
    login(data);
  };

  if (loading) return <div>Cargando...</div>;

  return (
    <BrowserRouter>
      <Routes>
        {/* Bienvenida ADNIA */}
        <Route path="/bienvenida" element={<BienvenidaADNIA />} />

        {/* Login / registro */}
        <Route path="/" element={!usuario ? <Login onLogin={handleLogin} /> : <Navigate to="/dashboard" />} />

        {/* Dashboard central ADNIA */}
        <Route path="/dashboard" element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } />

        {/* Paneles jurídicos protegidos */}
        <Route path="/fiscal" element={
          <ProtectedRoute>
            <PanelFiscal />
          </ProtectedRoute>
        } />
        <Route path="/penal" element={
          <ProtectedRoute>
            <PanelPenal />
          </ProtectedRoute>
        } />
        <Route path="/civil" element={
          <ProtectedRoute>
            <PanelCivil />
          </ProtectedRoute>
        } />
        <Route path="/social" element={
          <ProtectedRoute>
            <PanelSocial />
          </ProtectedRoute>
        } />
        <Route path="/administrativo" element={
          <ProtectedRoute>
            <PanelAdministrativo />
          </ProtectedRoute>
        } />

        {/* Panel de subida/análisis de documentos */}
        <Route path="/subida" element={
          <ProtectedRoute>
            <PanelSubida />
          </ProtectedRoute>
        } />

        {/* Paneles extra: favoritos, alertas, memoria, blockchain, auditoría, etc */}
        <Route path="/favoritos" element={
          <ProtectedRoute>
            <PanelFavoritos />
          </ProtectedRoute>
        } />
        <Route path="/alertas" element={
          <ProtectedRoute>
            <PanelAlertas />
          </ProtectedRoute>
        } />
        <Route path="/auditoria" element={
          <ProtectedRoute>
            <PanelAuditoria />
          </ProtectedRoute>
        } />
        <Route path="/blockchain" element={
          <ProtectedRoute>
            <PanelBlockchain />
          </ProtectedRoute>
        } />
        <Route path="/memoria" element={
          <ProtectedRoute>
            <PanelMemoria />
          </ProtectedRoute>
        } />
        <Route path="/memoria-editable" element={
          <ProtectedRoute>
            <PanelMemoriaEditable />
          </ProtectedRoute>
        } />
        <Route path="/espia" element={
          <ProtectedRoute>
            <PanelEspia />
          </ProtectedRoute>
        } />

        {/* Panel Admin solo para rol "admin" */}
        <Route path="/admin" element={
          rol === "admin"
            ? <PanelAdmin />
            : <Navigate to="/dashboard" />
        } />

        {/* Cualquier ruta desconocida redirige a bienvenida */}
        <Route path="*" element={<Navigate to="/bienvenida" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default MainApp;
