import React from "react";
import MainApp from "./MainApp";
import "./App.css";

function App() {
  return (
    <div className="adnia-app" style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #061727 60%, #0e2a44 100%)",
      fontFamily: "Montserrat, Arial, sans-serif"
    }}>
      <MainApp />
    </div>
  );
}

export default App;
