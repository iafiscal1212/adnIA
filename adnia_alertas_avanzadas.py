# adnia_alertas_avanzadas.py
import json
from flask import Flask, jsonify, request
from datetime import datetime
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)


def cargar_archivo(nombre):
    try:
        with open(nombre, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️ Error cargando {nombre}: {e}")
        return []

@app.route("/alertas")
def alertas():
    memoria = cargar_archivo("adnia_memory.json")
    trampas = cargar_archivo("trampas_legales.json")
    constitucion = cargar_archivo("constitucion_espanola_base.json")

    resultados = []
    if not memoria.get("boe_alertas"):
        return jsonify(resultados)

    ultima = memoria["boe_alertas"][-1]
    titulares = ultima["titulares"]

    for t in titulares:
        alerta = {"titular": t}
        for r in trampas:
            if r["clave"].lower() in t.lower():
                alerta["trampa"] = r["riesgo"]

        for art in constitucion:
            if any(p in t.lower() for p in art["texto"].lower().split()[:12]):
                alerta["constitucion"] = art

        resultados.append(alerta)

    return jsonify(resultados)

@app.route("/escanear", methods=["POST"])
def escanear():
    try:
        subprocess.run(["python", "adnia_boe_scanner.py"], check=True)
        return "✅ Escaneo completado y memoria actualizada."
    except subprocess.CalledProcessError as e:
        return f"❌ Error al ejecutar el escaneo: {e}"

if __name__ == "__main__":
    app.run(port=3002)
