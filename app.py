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
from langchain_core.prompts import PromptTemplate

# --- NUESTRAS IMPORTACIONES ---
from blockchain_adnia import Blockchain
from legal_tools import *

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# --- CONFIGURACIÓN E INSTANCIAS ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
HUMBOT_API_KEY = os.getenv("HUMBOT_API_KEY")

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
                # --- SELECCIÓN DEL MODELO DE LENGUAJE ---
                if model_provider == "google":
                    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=GEMINI_API_KEY, temperature=0)
                elif model_provider == "openai":
                    llm = ChatOpenAI(model="gpt-4-turbo", openai_api_key=OPENAI_API_KEY, temperature=0)
                elif model_provider == "mistral":
                    llm = ChatMistralAI(model="mistral-large-latest", api_key=MISTRAL_API_KEY, temperature=0)
                else:
                    yield f"El modelo '{model_provider}' no es válido para el agente."
                    return

                # --- LISTA COMPLETA DE HERRAMIENTAS ---
                tools = [
                    consultar_base_de_conocimiento,
                    iniciar_protocolo_interrogatorio,
                    preguntar_al_usuario,
                    redactor_escritos_juridicos,
                    buscar_en_boe, 
                    consultar_estado_api_hacienda, 
                    consultar_jurisprudencia_y_guias_procesales,
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
                
                # --- BLOQUE DEL PROMPT PERSONALIZADO (con RAG + Interrogatorio) ---
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
                final_instructions = """
Your purpose is to act as an expert legal assistant for a lawyer. You must be proactive, structured, and base your conclusions on evidence.

**Your primary directive is to follow this exact workflow:**
1.  **Consult Knowledge Base:** For any legal question or drafting request, your first action MUST be to use the `consultar_base_de_conocimiento` tool to find relevant legal articles and jurisprudence. This step is mandatory to ground your reasoning.
2.  **Initiate Interrogation (if drafting):** After consulting the knowledge base, if the user wants to draft a document ('carta de despido', 'demanda', 'contrato', etc.), your next action MUST be to use the `iniciar_protocolo_interrogatorio` tool to get the list of necessary questions.
3.  **Ask Questions:** Once you have the list, you MUST use the `preguntar_al_usuario` tool to ask the user these questions ONE BY ONE. Wait for the user's answer before asking the next question.
4.  **Confirm and Draft:** After asking all questions and receiving all answers, you will say "Perfecto, tengo toda la información necesaria. Procedo a la redacción." Then, and only then, you will use the `redactor_escritos_juridicos` tool, providing it with all the information you have gathered.
5.  **Final Answer:** Your FINAL ANSWER must be the complete text of the drafted document or the direct answer to the user's query, grounded in the information from the knowledge base. Do not provide meta-commentary about your own process.
"""
                prompt_with_final_instructions = template.replace(
                    "Begin!", 
                    final_instructions + "\n\nBegin!"
                )
                prompt = PromptTemplate.from_template(prompt_with_final_instructions)
                agent = create_react_agent(llm, tools, prompt)
                agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=25)

                # --- LÓGICA DE HISTORIAL E INVOCACIÓN ---
                chat_history = []
                for msg in chat_history_json:
                    if msg["role"] == "user":
                        chat_history.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "ai":
                        chat_history.append(AIMessage(content=msg["content"]))
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

# --- OTRAS RUTAS DE LA APP ---
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
        return jsonify({"message": analisis_resultado})
    else:
        return jsonify({"error": "Formato de archivo no permitido"}), 400

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
