import os
import json
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

from humanshield_module_adnia import humanize_with_humbot

# --- Herramientas de Búsqueda en Fuentes Oficiales ---

# 1. Herramienta principal para el BOE
buscar_en_boe = TavilySearchResults(
    max_results=3,
    name="buscar_en_boe",
    description="Busca en el Boletín Oficial del Estado (BOE) para encontrar leyes, reales decretos, y legislación nacional vigente."
)
# Forzamos que la búsqueda sea solo en el sitio del BOE
buscar_en_boe.search_kwargs = {"query_prefix": "site:boe.es"}

# 2. Herramienta para la Seguridad Social
buscar_en_seguridad_social = TavilySearchResults(
    max_results=2,
    name="buscar_en_seguridad_social",
    description="Busca en la web de la Seguridad Social española sobre trámites, pensiones, cotizaciones, etc."
)
buscar_en_seguridad_social.search_kwargs = {"query_prefix": "site:seg-social.es OR site:inclusion.gob.es"}

# 3. Herramienta para la Agencia Tributaria (Hacienda)
buscar_en_hacienda = TavilySearchResults(
    max_results=2,
    name="buscar_en_hacienda",
    description="Busca en la web de la Agencia Tributaria española (Hacienda) sobre impuestos, IRPF, IVA, y procedimientos fiscales."
)
buscar_en_hacienda.search_kwargs = {"query_prefix": "site:agenciatributaria.gob.es"}

# 4. Herramienta para la Unión Europea
buscar_normativa_europea = TavilySearchResults(
    max_results=2,
    name="buscar_normativa_europea",
    description="Busca en el portal de legislación de la Unión Europea (EUR-Lex) para encontrar directivas y reglamentos europeos."
)
buscar_normativa_europea.search_kwargs = {"query_prefix": "site:eur-lex.europa.eu"}


# Lista completa de herramientas que los agentes podrán usar
tools = [
    buscar_en_boe,
    buscar_en_seguridad_social,
    buscar_en_hacienda,
    buscar_normativa_europea
]

# --- Fábrica de LLMs ---
def get_llm(model_provider: str):
    """Crea una instancia del LLM basado en el proveedor elegido."""
    if model_provider == "openai":
        return ChatOpenAI(temperature=0.7, model="gpt-4o", streaming=True)
    elif model_provider == "mistral":
        return ChatMistralAI(model="mistral-large-latest", temperature=0.7, streaming=True)
    elif model_provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7, streaming=True)
    return ChatOpenAI(temperature=0.7, model="gpt-4o", streaming=True)

# --- Plantilla de Prompt ---
prompt_template = """Eres ADNIA, una IA experta en derecho español y europeo. Tu especialidad es: {jurisdiccion}.
Tu misión es dar respuestas precisas y actualizadas. Para ello, eres proactiva y utilizas las herramientas de búsqueda en fuentes oficiales (BOE, Seguridad Social, Hacienda, EUR-Lex) ANTES de dar una respuesta definitiva si la pregunta trata sobre leyes, decretos, normativas o procedimientos actuales.
Basa tus respuestas en los resultados de la búsqueda para ser preciso y no alucinar. Cita siempre la fuente que has consultado.

Tienes acceso a las siguientes herramientas:
{tools}

Historial de la conversación: {chat_history}
Pregunta del usuario: {input}
Tu respuesta (Pensamiento, Acción, Observación...): {agent_scratchpad}
"""
prompt = ChatPromptTemplate.from_template(prompt_template)

# --- Creación dinámica de agentes ---
def get_agent_executor(jurisdiction: str, model_provider: str):
    llm = get_llm(model_provider)
    tool_names = ", ".join([t.name for t in tools])
    # Hacemos el prompt específico para la jurisdicción y le pasamos las herramientas
    specific_prompt = prompt.partial(jurisdiccion=jurisdiction, tools=tools, tool_names=tool_names)
    agent = create_structured_chat_agent(llm, tools, specific_prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

# --- Función principal de Chat ---
def run_agent_chat_and_humanize(message: str, chat_history: list, jurisdiction: str, model_provider: str, humanize: bool):
    agent_executor = get_agent_executor(jurisdiction, model_provider)
    agent_input = {"input": message, "chat_history": chat_history}
    
    # Obtenemos la respuesta completa del agente
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
