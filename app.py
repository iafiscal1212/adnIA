import os
import traceback
import json
from flask import Flask, request, jsonify, Response, stream_with_context, send_from_directory
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import logging
from datetime import datetime
import pypdf

# --- IMPORTACIONES DE LANGCHAIN ---
from langchain_core.messages import HumanMessage, AIMessage
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_mistralai import ChatMistralAI
# Importación añadida para el prompt personalizado
from langchain_core.prompts import PromptTemplate

# --- NUESTRAS IMPORTACIONES ---
from blockchain_adnia import Blockchain
# Asegúrate de que legal_tools.py está en la misma carpeta y contiene todas las herramientas
from legal_tools import *

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# --- CONFIGURACIÓN DE LAS CLAVES DE API ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
HUMBOT_API_KEY = os.getenv("HUMBOT_API_KEY")

# --- INSTANCIACIÓN DE LA BLOCKCHAIN ---
blockchain = Blockchain()

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# --- RUTAS DE LA APLICACIÓN ---
@app.route("/")
def home():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/chat.html")
def chat_page():
    return send_from_directory(app.static_folder, "chat.html")

@app.route("/admin.html")
def admin_page():
    return send_from_directory(app.static_folder, "admin.html")

# --- API DE CHAT CON AGENTE ---
@app.route("/api/chat", methods=["POST"])
def handle_chat():
    try:
        data = request.get_json()
        message_text = data.get("message")
        model_provider = data.get("model", "google")
        
        if not message_text:
            return Response("El mensaje no puede estar vacío.", status=400)

        blockchain.add_transaction(
            action_details=f"Consulta con Agente ({model_provider}): {message_text[:50]}...",
            user="Abogado (Cliente Demo)"
        )
        blockchain.mine_block()
        
        chat_history_json = data.get("chat_history", [])
        
        def generate_ai_response():
            llm = None
            try:
                # --- SELECCIÓN DEL MODELO DE LENGUAJE (LLM) PARA EL AGENTE ---
                if model_provider == "google":
                    if not GEMINI_API_KEY: yield "Error: GOOGLE_API_KEY no configurada."; return
                    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY, temperature=0)
                
                elif model_provider == "openai":
                    if not OPENAI_API_KEY: yield "Error: OPENAI_API_KEY no configurada."; return
                    llm = ChatOpenAI(model="gpt-4-turbo", openai_api_key=OPENAI_API_KEY, temperature=0)

                elif model_provider == "mistral":
                    if not MISTRAL_API_KEY: yield "Error: MISTRAL_API_KEY no configurada."; return
                    llm = ChatMistralAI(model="mistral-large-latest", api_key=MISTRAL_API_KEY, temperature=0)
                
                elif model_provider == "humbot":
                    yield "El modelo Humbot no tiene una integración directa con LangChain en esta versión. Por favor, selecciona otro modelo."
                    return
                
                else:
                    yield f"El modelo '{model_provider}' no es válido para el agente."
                    return

                # --- CONFIGURACIÓN DEL AGENTE CON TODAS LAS HERRAMIENTAS ---
                tools = [
                    buscar_en_boe, 
                    consultar_estado_api_hacienda, 
                    consultar_jurisprudencia_y_guias_procesales,
                    redactor_escritos_juridicos,
                    herramienta_experto_derecho_social,
                    herramienta_experto_derecho_civil,
                    herramienta_experto_derecho_europeo,
                    herramienta_experto_derecho_espanol,
                    herramienta_experto_derecho_administrativo,
                    analizador_documental_sherlock,
                    simulador_sala_de_vistas,
                    analista_estrategico_praetorian,
                    motor_razonamiento_logos,
                    protocolo_genesis_estrategia_completa
                ]
                
                # --- BLOQUE DEL PROMPT PERSONALIZADO (LA MODIFICACIÓN CLAVE) ---

                # La plantilla base del agente ReAct
                template = """
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

                # Añadimos la instrucción clave al final de la plantilla
                final_instructions = """
Your purpose is to act as an expert legal assistant for a lawyer.
After using your tools and gathering all necessary information, you MUST formulate a final, comprehensive response that directly fulfills the user's original request.
- If the user asked for a document to be drafted, your FINAL ANSWER must be the complete text of that document.
- Do not provide meta-commentary about your own process or suggest consulting another lawyer. Your user is the lawyer.
- Synthesize all the information you've gathered into a practical, definitive final output.
"""

                # Insertamos nuestras instrucciones en la plantilla original
                prompt_with_final_instructions = template.replace(
                    "Begin!", 
                    final_instructions + "\n\nBegin!"
                )

                # Creamos el prompt final a partir de la plantilla modificada
                prompt = PromptTemplate.from_template(prompt_with_final_instructions)

                # Creamos el agente y el ejecutor con el nuevo prompt
                agent = create_react_agent(llm, tools, prompt)
                agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)


                # --- CONSTRUCCIÓN DEL HISTORIAL PARA EL AGENTE ---
                chat_history = []
                for msg in chat_history_json:
                    if msg["role"] == "user":
                        chat_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "ai":
                        chat_history.append(AIMessage(content=msg["content"]))

                # --- INVOCACIÓN DEL AGENTE ---
                response = agent_executor.invoke({
                    "input": message_text,
                    "chat_history": chat_history
                })
                
                yield response['output']

            except Exception as e:
                logging.error(f"Error durante la ejecución del agente ({model_provider}): {traceback.format_exc()}")
                yield f"Error al procesar la solicitud con el agente."

        return Response(stream_with_context(generate_ai_response()), mimetype='text/plain; charset=utf-8')

    except Exception as e:
        app.logger.error(traceback.format_exc())
        return Response(f"Error interno del servidor: {e}", status=500)

# --- RUTA DE SUBIDA DE ARCHIVOS ---
@app.route("/api/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files: return jsonify({"error": "No se encontró el archivo"}), 400
    file = request.files['file']
    if file.filename == '': return jsonify({"error": "Ningún archivo seleccionado"}), 400
    
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        blockchain.add_transaction(f"Documento analizado: {filename}", "Abogado (Cliente Demo)")
        blockchain.mine_block()

        analisis_resultado = f"Archivo '{filename}' subido con éxito."
        try:
            if filename.lower().endswith('.pdf'):
                texto_extraido = ""
                with open(filepath, 'rb') as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        texto_extraido += page.extract_text() or ""
                
                if texto_extraido:
                    # Usamos la herramienta directamente para el análisis
                    analisis_resultado = analizador_documental_sherlock.run(texto_extraido)
                else:
                    analisis_resultado += " No se pudo extraer texto del PDF para su análisis."
            
        except Exception as e:
            logging.error(f"Error durante el análisis del documento: {e}")
            analisis_resultado += " Ocurrió un error durante el análisis del documento."

        return jsonify({"message": analisis_resultado})
    else:
        return jsonify({"error": "Formato de archivo no permitido"}), 400

# --- RUTA DE AUDITORÍA ---
@app.route("/api/audit")
def get_audit_log():
    try:
        chain_data = list(reversed(blockchain.chain))
        flat_logs = []
        for block in chain_data:
            for tx in block['transactions']:
                flat_logs.append({'timestamp': tx.get('timestamp', datetime.fromtimestamp(block['timestamp']).isoformat()), 'action': tx['action'], 'user': tx['user'], 'block_index': block['index'], 'block_hash': block['hash']})
        return jsonify(flat_logs)
    except Exception as e:
        app.logger.error(f"Error al obtener registros de auditoría: {e}")
        return jsonify({"error": "No se pudieron obtener los registros"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host="0.0.0.0", port=port)
