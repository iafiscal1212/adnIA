# adnia_agents.py (VERSIÓN DEFINITIVA CORREGIDA CON LANGCHAIN-TAVILY - JULIO 2025)

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
from langchain_tavily import TavilySearch  # CORRECCIÓN: Nuevo import correcto (instala langchain-tavily)

# Asumimos que este módulo existe
from humanshield_module_adnia import humanize_with_humbot

# --- Herramientas de los Agentes ---
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

# CORRECCIÓN: Instanciación correcta con tu key para evitar validation error
_tavily_search_base = TavilySearch(
    max_results=3,
    tavily_api_key="CN3YWGYR7WZM18Y9A7VQFLMD"  # Tu key aquí para testing; cambia a os.getenv("TAVILY_API_KEY") en prod
)

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
- Jamás repitas que eres una IA ni uses frases genéricas: tu voz es firme y fundamentada.
- Fundamenta con artículos, sentencias, directivas, etc. Cita fuentes siempre que sea posible.
- Cuando detectes un abuso o laguna legal, proponlo y sugiere cómo aprovecharlo.
- Sé creativa y estratégica.
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
def get_agent_executor(llm, tools, prompt_template, context):
    """Crea un agente y su ejecutor con el contexto completo."""
    # Inyectamos el contexto en la plantilla del prompt
    final_prompt = prompt_template.partial(**context)
    
    agent = create_structured_chat_agent(llm, tools, final_prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

# --- Función Principal de Chat ---
def run_agent_chat_and_humanize(message, chat_history, jurisdiction, model_provider, humanize, context):
    """Ejecuta el chat del agente."""
    
    llm = get_llm(model_provider)

    # El contexto específico de la consulta se añade aquí
    full_context = {
        **context,
        "jurisdiccion": jurisdiction,
    }

    agent_executor = get_agent_executor(llm, tools, prompt, full_context)
    
    # El input del agente necesita el mensaje y el historial
    agent_input = {
        "input": message,
        "chat_history": chat_history,
    }
    
    response = agent_executor.invoke(agent_input)
    raw_output = response.get("output", "El agente no produjo una respuesta.")
    
    if humanize:
        yield "Humanizando con HumanShield... "
        humanized_result = humanize_with_humbot(raw_output)
        yield humanized_result.get("humanized", raw_output)
    else:
        yield raw_output
