import os
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub # Importamos hub para cargar prompts probados

from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.document_loaders import PyPDFLoader
from PIL import Image
import pytesseract
from humanshield_module_adnia import humanize_with_humbot

# --- Herramientas de los Agentes ---
@tool
def analyze_document(file_path: str) -> str:
    """
    Analiza el contenido de un archivo (PDF o imagen) localmente y devuelve el texto extraído.
    Utiliza esta herramienta cuando el usuario pregunte sobre un documento que acaba de subir.
    """
    # El código de esta herramienta no necesita cambios
    try:
        uploads_dir = "uploads"
        # Creamos una ruta segura para evitar que se acceda a otros directorios
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

# CORRECCIÓN 1: Envolvemos Tavily en una función @tool
_tavily_search = TavilySearchResults(max_results=3)

@tool
def buscar_en_boe(query: str) -> str:
    """Busca en el Boletín Oficial del Estado (BOE). Utiliza esta herramienta para encontrar leyes, decretos, y otra información oficial española."""
    site_restricted_query = f"site:boe.es {query}"
    return _tavily_search.invoke(site_restricted_query)

tools = [analyze_document, buscar_en_boe]

# --- Fábrica de LLMs (CORRECCIÓN 2) ---
def get_llm(model_provider: str):
    """Obtiene el modelo de lenguaje (LLM) asegurándose de usar la API Key correcta."""
    if model_provider == "openai":
        return ChatOpenAI(temperature=0.7, model="gpt-4o")
    elif model_provider == "mistral":
        return ChatMistralAI(model="mistral-large-latest", temperature=0.7)
    elif model_provider == "gemini":
        # La librería busca la variable de entorno 'GOOGLE_API_KEY'
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7)
    return ChatOpenAI(temperature=0.7, model="gpt-4o")

# --- Creación de Agente (CORRECCIÓN 3) ---
def get_agent_executor(jurisdiction: str, model_provider: str):
    """Crea un agente y su ejecutor para una jurisdicción y LLM específicos."""
    
    # Usamos un prompt estándar de LangChain que ya está preparado para agentes
    # Esto soluciona el error de "missing required variables"
    prompt = hub.pull("hwchase17/structured-chat-agent")

    # Reemplazamos el mensaje de sistema del prompt estándar por el nuestro
    prompt.messages[0].prompt.template = (
        "Eres ADNIA, una IA experta en derecho español y europeo. "
        f"Tu especialidad actual es: {jurisdiction}.\n"
        "Responde a las consultas del usuario de manera precisa y directa. "
        "Antes de responder, utiliza las herramientas de búsqueda si la pregunta requiere información legal específica, "
        "novedosa o sobre legislación vigente. Basa tus respuestas en los resultados de la búsqueda para ser preciso y no alucinar."
    )

    llm = get_llm(model_provider)
    agent = create_structured_chat_agent(llm, tools, prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True
    )

# --- Función Principal de Chat ---
def run_agent_chat_and_humanize(message: str, chat_history: list, jurisdiction: str, model_provider: str, humanize: bool):
    # Esta función no necesita cambios
    agent_executor = get_agent_executor(jurisdiction, model_provider)
    agent_input = {"input": message, "chat_history": chat_history}
    
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
