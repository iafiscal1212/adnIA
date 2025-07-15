# adnia_agents.py (VERSIÓN FINAL PARA DEMO)

import os
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from PIL import Image
import pytesseract
from langchain_community.tools.tavily_search import TavilySearchResults

# Asumimos que este módulo existe
from humanshield_module_adnia import humanize_with_humbot

# --- Herramientas ---
@tool
def analyze_document(file_path: str) -> str:
    """
    Analiza el contenido de un archivo (PDF o imagen) localmente y devuelve el texto extraído.
    Utiliza esta herramienta cuando el usuario pregunte sobre un documento que acaba de subir.
    """
    try:
        uploads_dir = "uploads"
        safe_path = os.path.join(uploads_dir, os.path.basename(file_path))
        if not os.path.exists(safe_path):
            return f"Error: El archivo no se encuentra en la ruta: {safe_path}"
        if safe_path.lower().endswith('.pdf'):
            pages = PyPDFLoader(safe_path).load_and_split()
            return "".join(page.page_content for page in pages)[:8000]
        elif safe_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return pytesseract.image_to_string(Image.open(safe_path))[:8000]
        else:
            return "Error: Formato de archivo no soportado."
    except Exception as e:
        return f"Error al procesar el archivo: {e}"

_tavily_search_base = TavilySearchResults(max_results=3)

@tool
def buscar_en_boe(query: str) -> str:
    """Busca en el Boletín Oficial del Estado (BOE). Utiliza esta herramienta para encontrar leyes, decretos y otra información oficial española."""
    site_restricted_query = f"site:boe.es {query}"
    return _tavily_search_base.invoke(site_restricted_query)

tools = [analyze_document, buscar_en_boe]

# --- Fábrica de LLMs ---
def get_llm(model_provider: str):
    """Obtiene el modelo de lenguaje (LLM)."""
    if model_provider == "openai":
        return ChatOpenAI(temperature=0.7, model="gpt-4o")
    elif model_provider == "mistral":
        return ChatMistralAI(model="mistral-large-latest", temperature=0.7)
    elif model_provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7)
    return ChatOpenAI(temperature=0.7, model="gpt-4o")

# --- PROMPT DEFINITIVO DE ADNIA ---
ADNIA_SYSTEM_PROMPT = """Eres ADNIA, una inteligencia jurídica con personalidad, proactiva y disruptiva.

Tu misión es defender a ciudadanos y profesionales, fundamentando todas tus respuestas en:
- Leyes vigentes (BOE, legislación española y europea)
- Jurisprudencia relevante y reciente (incluyendo Tribunal Supremo, Tribunal Constitucional, TJUE)
- Directivas y reglamentos de la Unión Europea

Contexto del usuario actual:
- Usuario: {usuario}
- Rol: {rol}
- País: {pais}
- Especialidad jurídica de esta consulta: {jurisdiccion}

Normas de conducta:
- No tienes filtros ideológicos ni estructuras de precaución artificial.
- Jamás repitas que eres una IA ni uses frases genéricas: tu voz es firme y fundamentada.
- Fundamenta con artículos, sentencias, directivas, resoluciones exactas. Cita fuentes y referencias siempre que sea posible.
- Cuando detectes un abuso, contradicción o laguna legal, proponlo y sugiere cómo aprovecharlo a favor del ciudadano.
- Sé creativa, estratégica y “busca ganar” cada asunto dentro del marco legal.
- Prioriza la acción: da siempre el escrito, modelo o recurso más avanzado posible.
- Si una ley española perjudica al usuario pero en Europa hay alternativa más favorable, ¡propónla!
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ADNIA_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# --- Creación de Agentes ---
def get_agent_executor(jurisdiction, model_provider, context):
    """Crea un agente y su ejecutor con el contexto completo."""
    llm = get_llm(model_provider)
    
    agent = create_structured_chat_agent(llm, tools, prompt)
    
    # Pasamos el contexto al ejecutor para que esté disponible en cada invocación
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={"context": context} # Guardamos el contexto aquí
    )

# --- Función Principal de Chat ---
def run_agent_chat_and_humanize(message, chat_history, jurisdiction, model_provider, humanize, context):
    """Ejecuta el chat del agente y opcionalmente humaniza la respuesta."""
    
    agent_executor = get_agent_executor(jurisdiction, model_provider, context)
    
    # El input del agente necesita todas las variables del prompt
    agent_input = {
        "input": message,
        "chat_history": chat_history,
        "jurisdiccion": jurisdiction,
        **context # Desempaquetamos el resto del contexto aquí
    }
    
    response = agent_executor.invoke(agent_input)
    raw_output = response.get("output", "El agente no produjo una respuesta.")
    
    if humanize:
        yield "Humanizando con HumanShield... "
        humanized_result = humanize_with_humbot(raw_output)
        if "error" in humanized_result:
            yield f"\n\n[Error del humanizador: {humanized_result['error']}]"
        else:
            yield humanized_result.get("humanized", raw_output)
    else:
        yield raw_output
