# app.py (Versión Final para la Demo)

import os
import traceback
import json
from flask import Flask, request, jsonify, Response, stream_with_context, render_template
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

from adnia_agents import run_agent_chat_and_humanize
from blockchain_adnia import guardar_en_blockchain

load_dotenv()

# --- CONFIGURACIÓN ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='static', template_folder='static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- RUTAS ---
@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/chat.html")
def chat_page():
    return app.send_static_file("chat.html")

# --- API ENDPOINTS ---
@app.route("/api/chat", methods=["POST"])
def handle_chat():
    try:
        data = request.get_json()
        message = data.get("message")
        model_provider = data.get("model", "openai")
        jurisdiction = data.get("jurisdiction", "general")
        humanize = data.get("humanize", False)
        
        if not message:
            return Response("El mensaje no puede estar vacío.", status=400)

        guardar_en_blockchain(f"Consulta registrada: {message[:50]}...")
        
        chat_history = data.get("chat_history", [])

        # --- CONTEXTO PARA LA PERSONALIDAD DE ADNIA ---
        # Para la demo, usamos valores fijos. En el futuro, esto vendría
        # de una base de datos de usuarios.
        user_context = {
            "usuario": "Abogado Cliente (Demo)",
            "rol": "profesional",
            "pais": "España",
            "memoriaLarga": "(sin memoria estratégica activa para esta demo)",
            "favoritos": "(sin favoritos guardados para esta demo)"
        }

        def generate_response():
            # Pasamos el contexto del usuario a la función del agente
            for chunk in run_agent_chat_and_humanize(message, chat_history, jurisdiction, model_provider, humanize, user_context):
                yield chunk

        return Response(stream_with_context(generate_response()), mimetype='text/plain; charset=utf-8')

    except Exception as e:
        print(traceback.format_exc())
        return Response(f"Error interno del servidor: {str(e)}", status=500)

@app.route("/api/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Ningún archivo seleccionado"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        guardar_en_blockchain(f"Documento analizado: {filename}")
        
        return jsonify({"message": "Archivo subido correctamente.", "filepath": filepath})
    else:
        return jsonify({"error": "Formato de archivo no permitido"}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
