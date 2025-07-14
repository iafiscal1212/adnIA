import os
import json
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

# Librerías para procesamiento local de documentos
from langchain_community.document_loaders import PyPDFLoader
from PIL import Image
import pytesseract

from humanshield_module_adnia import humanize_with_humbot

# --- Herramientas de los Agentes ---

@tool
def analyze_document(file_path: str) -> str:
    """
    Analiza el contenido de un archivo (PDF o imagen) localmente y devuelve el texto extraído.
    Utiliza esta herramienta para leer documentos y responder preguntas basadas en su contenido.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: El archivo no se encuentra en la ruta especificada: {file_path}"

        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            text = "".join(page.page_content for page in pages)
            return text[:4000]
        elif file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return text[:4000]
        else:
            return "Error: Formato de archivo no soportado. Solo se admiten PDF e imágenes."
    except Exception as e:
        return f"Error al procesar el archivo: {e}"

# --- Herramientas de Búsqueda Web ---
buscar_en_boe = TavilySearchResults(max_results=3, name="buscar_en_boe", description="Busca en el Boletín Oficial del Estado (BOE).")
buscar_en_boe.search_kwargs = {"query_prefix": "site:boe.es"}

# ... (Aquí irían tus otras herramientas de búsqueda) ...

# Lista completa de herramientas
tools = [
    analyze_document, 
    buscar_en_boe,
    # ... (y las demás herramientas de búsqueda)
]

# --- Fábrica de LLMs ---
def get_llm(model_provider: str):
    """Crea una instancia del LLM basado en el proveedor elegido."""
    api_key_map = {
        "openai": "OPENAI_API_KEY",
        "mistral": "MISTRAL_API_KEY",
        "gemini": "GEMINI_API_KEY"
    }
    api_key = os.getenv(api_key_map.get(model_provider))
    if not api_key and model_provider != "gemini": # Gemini puede usar credenciales de gcloud
        raise ValueError(f"La variable de entorno {api_key_map.get(model_provider)} no está configurada.")

    if model_provider == "openai":
        return ChatOpenAI(api_key=api_key, temperature=0.7, model="gpt-4o", streaming=True)
    elif model_provider == "mistral":
        return ChatMistralAI(api_key=api_key, model="mistral-large-latest", temperature=0.7, streaming=True)
    elif model_provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, streaming=True)
    else:
        return ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), temperature=0.7, model="gpt-4o", streaming=True)

# --- El resto del archivo (Prompt, Agentes, etc.) se mantiene como en la última versión ---
# ...
