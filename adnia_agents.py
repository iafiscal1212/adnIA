import os
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from PIL import Image
import pytesseract
import json

# --- Configuración del LLM ---
# Asegúrate de que la variable de entorno OPENAI_API_KEY esté configurada.
llm = ChatOpenAI(temperature=0.7, model="gpt-4o")

# --- Herramientas de los Agentes ---
@tool
def analyze_document(file_path: str) -> str:
    """
    Analiza el contenido de un archivo (PDF o imagen PNG) y devuelve el texto extraído.
    Utiliza esta herramienta para leer documentos y responder preguntas basadas en su contenido.
    """
    try:
        if not os.path.exists(file_path):
            return f"Error: El archivo no se encuentra en la ruta especificada: {file_path}"

        if file_path.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path)
            pages = loader.load_and_split()
            text = "".join(page.page_content for page in pages)
            return text[:4000]  # Limita la salida para no exceder los límites del prompt
        elif file_path.lower().endswith('.png'):
            img = Image.open(file_path)
            text = pytesseract.image_to_string(img)
            return text[:4000]
        else:
            return "Error: Formato de archivo no soportado. Solo se admiten .pdf y .png."
    except Exception as e:
        return f"Error al procesar el archivo: {e}"

tools = [analyze_document]

# --- Prompt para los Agentes Especializados ---
prompt_template = """Eres ADNIA, una IA experta en derecho español. Tu especialidad es: {jurisdiccion}.

Tu misión es responder a las consultas de los usuarios de manera precisa y directa, basándote en tu conocimiento y en cualquier documento proporcionado.

Instrucciones:
1.  **Analiza la pregunta:** Comprende la necesidad del usuario.
2.  **Usa tus herramientas si es necesario:** Si el usuario menciona un archivo, utiliza la herramienta `analyze_document` para examinarlo. No inventes contenido de archivos.
3.  **Responde con claridad:** Proporciona una respuesta concisa y bien fundamentada.

Historial de la conversación:
{chat_history}

Pregunta del usuario:
{input}

Tu respuesta (en formato de pensamiento y acción del agente):
{agent_scratchpad}
"""

prompt = ChatPromptTemplate.from_template(prompt_template)

# --- Creación de Agentes Especializados ---
jurisdicciones = [
    "Derecho Fiscal",
    "Derecho Penal",
    "Derecho Civil",
    "Derecho Social",
    "Derecho Administrativo",
    "Panel de Control"
]

agentes = {}
for jur in jurisdicciones:
    # Crear un prompt específico para cada jurisdicción
    specific_prompt = prompt.partial(jurisdiccion=jur)
    # Crear el agente
    agent = create_structured_chat_agent(llm, tools, specific_prompt)
    # Crear el ejecutor del agente
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,  # Útil para depuración
        handle_parsing_errors=True # Maneja errores de parseo del agente
    )
    agentes[jur.lower().replace(" ", "_").replace("derecho_", "")] = agent_executor


# --- Orquestador / Router ---
class RouteQuery(BaseModel):
    """Decide a qué jurisdicción o jurisdicciones enviar la pregunta del usuario."""
    jurisdicciones: list[str] = Field(..., description=f"Una o más de las siguientes jurisdicciones: {', '.join(jurisdicciones)}")

# El LLM de enrutamiento decidirá qué agente usar
router_llm = ChatOpenAI(temperature=0, model="gpt-4o")
structured_llm_router = router_llm.with_structured_output(RouteQuery)

router_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Eres un experto en enrutar preguntas de derecho español a la jurisdicción correcta."),
        ("human", "Enruta la siguiente pregunta del usuario a la(s) jurisdicción(es) más adecuada(s) de esta lista: {jurisdicciones_list}"),
        ("human", "{input}"),
    ]
)

# Cadena de enrutamiento
agent_router = (
    {"jurisdicciones_list": lambda x: json.dumps(jurisdicciones), "input": lambda x: x["input"]}
    | router_prompt
    | structured_llm_router
)

def run_agent_chat(message: str, chat_history: list, file_path: str = None):
    """
    Función principal que enruta y ejecuta el chat con los agentes.
    """
    # 1. Determinar el agente a utilizar
    route = agent_router.invoke({"input": message})

    selected_jurisdictions = route.jurisdicciones

    if not selected_jurisdictions:
        return "No pude determinar a qué especialista legal dirigir tu consulta. Por favor, sé más específico."

    # 2. Preparar el input para el/los agente(s)
    agent_input = {"input": message, "chat_history": chat_history}
    if file_path:
        agent_input["input"] += f"\n\nPor favor, analiza este documento: {file_path}"

    # 3. Ejecutar el/los agente(s) y recopilar respuestas
    responses = []
    for jur_name in selected_jurisdictions:
        agent_key = jur_name.lower().replace(" ", "_").replace("derecho_", "")
        if agent_key in agentes:
            agent_executor = agentes[agent_key]
            try:
                response = agent_executor.invoke(agent_input)
                responses.append(f"**Respuesta de {jur_name}:**\n{response['output']}")
            except Exception as e:
                responses.append(f"Error al consultar al agente de {jur_name}: {e}")
        else:
            responses.append(f"No se encontró un agente para la jurisdicción: {jur_name}")

    # 4. Consolidar y devolver la respuesta final
    if len(responses) == 1:
        return responses[0]
    else:
        return "\n\n".join(responses)
