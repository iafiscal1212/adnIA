from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from datetime import datetime
import os
import json
import logging

from adnia_reasoning_engine import generar_respuesta_juridica

app = Flask(__name__, static_folder="centro-control-adnia/build", static_url_path="/")
CORS(app)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')

@app.route("/preguntar", methods=["POST"])
def preguntar():
    data = request.get_json()
    pregunta = data.get("pregunta", "").strip()
    if not pregunta:
        return jsonify({"respuesta": "⚠️ No se recibió ninguna pregunta."}), 400
    respuesta = generar_respuesta_juridica(pregunta)
    return jsonify({"respuesta": respuesta})

@app.route("/alertas", methods=["GET"])
def alertas():
    try:
        with open("adnia_alertas_legales.json", "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route("/long_memory.json", methods=["GET"])
def memoria():
    try:
        with open("adnia_memory.json", "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except:
        return jsonify([])

@app.route("/memoria", methods=["POST"])
def guardar_memoria():
    try:
        nueva_memoria = request.get_json()
        with open("adnia_memory.json", "w", encoding="utf-8") as f:
            json.dump(nueva_memoria, f, indent=2, ensure_ascii=False)
        return jsonify({"estado": "✅ Memoria actualizada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/manifesto.md", methods=["GET"])
def manifesto():
    try:
        with open("manifesto.md", "r", encoding="utf-8") as f:
            return f.read(), 200, {"Content-Type": "text/plain; charset=utf-8"}
    except Exception as e:
        return f"⚠️ No se pudo cargar el manifiesto: {e}", 500

@app.route("/estado", methods=["GET"])
def estado():
    return jsonify({
        "nombre": "ADNIA",
        "estado": "activo",
        "modo": "vigilancia",
        "fecha": datetime.utcnow().isoformat() + "Z"
    })

@app.route("/", defaults={"path": "index.html"})
@app.route("/<path:path>")
def serve_frontend(path):
    full_path = os.path.join(app.static_folder, path)
    if path != "" and os.path.exists(full_path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")

@app.route("/conversaciones/<usuario>.json", methods=["GET"])
def cargar_conversaciones(usuario):
    try:
        ruta = f"conversaciones_{usuario}.json"
        if not os.path.exists(ruta):
            return jsonify([])
        with open(ruta, "r", encoding="utf-8") as f:
            return jsonify(json.load(f))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/conversaciones/<usuario>.json", methods=["POST"])
def guardar_conversacion(usuario):
    try:
        nueva = request.get_json()
        ruta = f"conversaciones_{usuario}.json"
        historial = []
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                historial = json.load(f)
        historial.append(nueva)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(historial, f, indent=2, ensure_ascii=False)
        return jsonify({"estado": "✅ Conversación guardada"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=["POST"])
def login():
    try:
        credenciales = request.get_json()
        usuario = credenciales.get("usuario", "")
        clave = credenciales.get("clave", "")

        with open("usuarios.json", "r", encoding="utf-8") as f:
            todos = json.load(f)

        datos = next((u for u in todos if u["usuario"] == usuario and u["clave"] == clave), None)

        if datos:
            return jsonify({
                "estado": "✅ Acceso permitido",
                "rol": datos["rol"],
                "usuario": datos["usuario"]
            })
        else:
            return jsonify({"estado": "❌ Usuario o clave incorrectos"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/usuarios", methods=["GET", "POST"])
def usuarios():
    try:
        if request.method == "GET":
            with open("usuarios.json", "r", encoding="utf-8") as f:
                return jsonify(json.load(f))

        if request.method == "POST":
            nuevos = request.get_json()
            with open("usuarios.json", "w", encoding="utf-8") as f:
                json.dump(nuevos, f, indent=2, ensure_ascii=False)
            return jsonify({"estado": "✅ Usuarios actualizados"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3002, debug=True)
