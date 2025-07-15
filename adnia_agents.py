# adnia_agents.py (VERSIÓN MEJORADA CON LANGGRAPH - JULIO 2025)

import os
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader
from PIL import Image
import pytesseract
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated
from humanshield_module_adnia import humanize_with_humbot  # Asumimos existe

# --- Estado para LangGraph ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    context: dict  # Añadido para contexto persistente

# --- Herramientas (igual) ---
@tool
def analyze_document(file_path: str) -> str:
    """Analiza el contenido de un archivo (PDF o imagen) localmente y devuelve el texto extraído."""
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
    """Busca en el Boletín Oficial del Estado (BOE)."""
    site_restricted_query = f"site:boe.es {query}"
    return _tavily_search_base.invoke(site_restricted_query)

tools = [analyze_document, buscar_en_boe]

# --- Fábrica de LLMs (igual) ---
def get_llm(model_provider: str):
    if model_provider == "openai":
        return ChatOpenAI(temperature=0.7, model="gpt-4o")
    elif model_provider == "mistral":
        return ChatMistralAI(model="mistral-large-latest", temperature=0.7)
    elif model_provider == "gemini":
        return ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.7)
    return ChatOpenAI(temperature=0.7, model="gpt-4o")

# --- PROMPT (igual) ---
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
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# --- Creación de Agent con LangGraph (NUEVO: Reemplaza old agent) ---
def get_agent_graph(llm, tools, context):
    def agent(state: AgentState):
        chain = prompt | llm.bind_tools(tools)
        result = chain.invoke(state["messages"])
        return {"messages": [result]}

    workflow = StateGraph(state_schema=AgentState)
    workflow.add_node("agent", agent)
    workflow.add_node("tools", ToolNode(tools))

    workflow.add_edge("__start__", "agent")
    workflow.add_conditional_edges(
        "agent",
        lambda state: "tools" if state["messages"][-1].tool_calls else END,
        {"tools": "tools", END: END}
    )
    workflow.add_edge("tools", "agent")

    graph = workflow.compile()
    graph.get_graph().context = context  # Añade contexto persistente
    return graph

# --- Función Principal de Chat (Actualizada para LangGraph) ---
def run_agent_chat_and_humanize(message, chat_history, jurisdiction, model_provider, humanize, context):
    llm = get_llm(model_provider)
    full_context = {**context, "jurisdiccion": jurisdiction}

    graph = get_agent_graph(llm, tools, full_context)

    inputs = {"messages": chat_history + [("user", message)]}
    for output in graph.stream(inputs):
        if "agent" in output:
            raw_output = output["agent"]["messages"][0].content
            if humanize:
                yield "Humanizando con HumanShield... "
                humanized_result = humanize_with_humbot(raw_output)
                yield humanized_result.get("humanized", raw_output)
            else:
                yield raw_output
