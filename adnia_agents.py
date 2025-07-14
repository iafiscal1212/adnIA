import os
import json
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

# (El resto de tus imports y herramientas no cambian)
# ...

# --- Fábrica de LLMs (VERSIÓN MODIFICADA) ---
def get_llm(model_provider: str):
    """Crea una instancia del LLM basado en el proveedor elegido, cargando la API Key explícitamente."""
    if model_provider == "openai":
        # Forzamos la lectura de la variable de entorno de OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada.")
        return ChatOpenAI(api_key=api_key, temperature=0.7, model="gpt-4o", streaming=True)
        
    elif model_provider == "mistral":
        api_key = os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("La variable de entorno MISTRAL_API_KEY no está configurada.")
        return ChatMistralAI(api_key=api_key, model="mistral-large-latest", temperature=0.7, streaming=True)
        
    elif model_provider == "gemini":
        # Google GenAI usa GOOGLE_API_KEY por defecto, así que no hace falta pasarla explícitamente
        # si la variable de entorno ya está configurada
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, streaming=True)
        
    else:
        # Opción por defecto
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("La variable de entorno OPENAI_API_KEY no está configurada.")
        return ChatOpenAI(api_key=api_key, temperature=0.7, model="gpt-4o", streaming=True)

# --- El resto de tu código de adnia_agents.py no cambia ---
# ... (Mantén el resto del archivo como estaba) ...
