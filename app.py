import os
import traceback
from flask import Flask, request, jsonify, Response, stream_with_context
from dotenv import load_dotenv
from adnia_agents import run_agent_chat_and_humanize

load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')

# ... (Aquí va tu configuración de Flask, SQLAlchemy, CORS, etc. Mantenla como estaba) ...

@app.route("/")
def home():
    return app.send_static_file("index.html")

@app.route("/chat.html")
def chat_page():
    return app.send_static_file("chat.html")

@app.route("/api/chat", methods=["POST"])
def handle_chat():
    try:
        data = request.get_json()
        message = data.get("message")
        model_provider = data.get("model", "openai")
        jurisdiction = data.get("jurisdiction", "general") # Ejemplo, asegúrate que el frontend lo envía
        humanize = data.get("humanize", False)
        
        if not message:
            return Response("El mensaje no puede estar vacío.", status=400)

        chat_history = [] # La gestión del historial debe implementarse aquí

        def generate_response():
            for chunk in run_agent_chat_and_humanize(message, chat_history, jurisdiction, model_provider, humanize):
                yield chunk

        return Response(stream_with_context(generate_response()), mimetype='text/plain; charset=utf-8')

    except Exception as e:
        print(traceback.format_exc())
        return Response(f"Error interno del servidor: {str(e)}", status=500)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
