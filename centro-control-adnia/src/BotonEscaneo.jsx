function BotonEscaneo() {
  const escanear = async () => {
    const escaneo = await fetch("http://localhost:3002/escanear", {
      method: "POST",
      credentials: "include"
    });
    const razonamiento = await fetch("http://localhost:3002/alertas", {
      credentials: "include"
    });
    const resultado = await escaneo.text();
    alert(resultado);
    window.location.reload();
  };

  return (
    <div className="my-6 text-center">
      <button
        onClick={escanear}
        className="bg-gradient-to-r from-cyan-400 to-blue-600 text-black font-bold px-8 py-3 rounded-xl shadow-lg hover:scale-105 hover:brightness-110 transition-all duration-300 tracking-wide"
      >
        ⚛️ Escanear BOE + Analizar Cuántico
      </button>
    </div>
  );
}

export default BotonEscaneo;
