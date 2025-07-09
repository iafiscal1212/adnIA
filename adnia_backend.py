# 📌 Archivo: adnia_backend.py — con soporte para análisis de documentos subidos

from flask import Flask, jsonify, request, session
from flask_cors import CORS
import json
import datetime
from adnia_reasoning_engine import resolver_conflicto as motor_local
import requests
import os
from werkzeug.utils import secure_filename
import PyPDF2

MISTRAL_API_KEY = "tiBisSqMlsbNkkD81CrikFHDlQigv1BB"
UPLOAD_FOLDER = "uploads"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
app.secret_key = "clave-ultra-secreta"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route("/procesar-doc", methods=["POST"])
def procesar_documento():
    try:
        if 'documento' not in request.files:
            return jsonify({"error": "No se ha enviado ningún archivo"}), 400

        archivo = request.files['documento']
        if archivo.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400

        nombre_seguro = secure_filename(archivo.filename)
        ruta_guardado = os.path.join(app.config['UPLOAD_FOLDER'], nombre_seguro)
        archivo.save(ruta_guardado)

        texto_extraido = ""
        if nombre_seguro.lower().endswith(".pdf"):
            with open(ruta_guardado, "rb") as f:
                lector = PyPDF2.PdfReader(f)
                for pagina in lector.pages:
                    texto_extraido += pagina.extract_text() or ""
        elif nombre_seguro.lower().endswith(".txt"):
            with open(ruta_guardado, "r", encoding="utf-8") as f:
                texto_extraido = f.read()
        else:
            return jsonify({"error": "Formato no soportado (solo PDF o TXT)"}), 415

        return jsonify({"texto": texto_extraido.strip()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Resto del backend (login, resolver, memoria, alertas...)
# Aquí mantienes todo lo anterior tal como lo tienes funcionando.

if __name__ == "__main__":
    app.run(port=3002)