import os
import json
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

# Se usan librerías locales para el análisis, que es lo que está configurado
from langchain_community.document_loaders import PyPDFLoader
from PIL import Image
import pytesseract

from humanshield_module_adnia import humanize_with_humbot

# --- Herramientas de los Agentes ---
@tool
def analyze_document(file_path: str) -> str:
    """
    Analiza el contenido de un archivo (PDF o imagen) localmente y devuelve el texto extraído.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: El archivo no se encuentra en la ruta: {file_path}"
        if file_path.lower().endswith('.pdf'):
            pages = PyPDFLoader(file_path).load_and_split()
            return "".join(page.page_content for page in pages)[:8000]
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            return pytesseract.image_to_string(Image.open(file_path))[:8000]
        else:
            return "Error: Formato de archivo no soportado."
    except Exception as e:
        return f"Error al procesar el archivo: {e}"

buscar_en_boe = TavilySearchResults(max_results=3, name="buscar_en_boe", description="Busca en el Boletín Oficial del Estado (BOE).")
buscar_en_boe.search_kwargs = {"query_prefix": "site:boe.es"}

# ... (otras herramientas de búsqueda)

tools = [analyze_document, buscar_en_boe]

# --- Fábrica de LLMs ---
def get_llm(model_provider: str):
    # (Esta función se mantiene como en la versión anterior)
    api_key_map = {"openai": "OPENAI_API_KEY", "mistral": "MISTRAL_API_KEY"}
    api_key = os.getenv(api_key_map.get(model_provider))
    if not api_key and model_provider not in ["gemini"]:
        raise ValueError(f"Falta la variable de entorno: {api_key_map.get(model_provider)}")
    if model_provider == "openai":
        return ChatOpenAI(api_key=api_key, temperature=0.7, model="gpt-4o")
    elif model_provider == "mistral":
        return ChatMistralAI(api_key=api_key, model="mistral-large-latest", temperature=0.7)
    elif model_provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7)
    return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model="gpt-4o")

# --- ¡NUEVO! Plantilla de Prompt Corregida ---
# Esta es la estructura correcta que espera la función del agente
prompt = ChatPromptTemplate.from_messages(
    [
        ("system",
         "Eres ADNIA, una IA experta en derecho español y europeo. Tu especialidad es: {jurisdiccion}.\n"
         "Responde a las consultas del usuario de manera precisa y directa. Antes de responder, utiliza las herramientas de búsqueda si la pregunta requiere información legal específica, novedosa o sobre legislación vigente. Basa tus respuestas en los resultados de la búsqueda para ser preciso y no alucinar."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

# --- ¡NUEVO! Creación de Agentes Corregida ---
def get_agent_executor(jurisdiction: str, model_provider: str):
    llm = get_llm(model_provider)
    # Pasamos solo la jurisdicción. El agente se encargará del resto de variables.
    agent_prompt = prompt.partial(jurisdiccion=jurisdiction)
    agent = create_structured_chat_agent(llm, tools, agent_prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- Función Principal de Chat (sin cambios) ---
def run_agent_chat_and_humanize(message: str, chat_history: list, jurisdiction: str, model_provider: str, humanize: bool):
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
