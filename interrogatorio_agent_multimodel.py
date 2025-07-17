#!/usr/bin/env python3
"""
Script para iniciar un agente de LangChain con múltiples proveedores de LLM,
actualizado a las prácticas modernas de LangChain (julio de 2025).
"""
from dotenv import load_dotenv
import os

# 0) Carga variables de entorno desde .env
load_dotenv()

# --- 1) Importaciones Modernas ---
# Se importan los modelos de Chat específicos de cada paquete
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI

# Se importan las funciones y clases modernas para crear agentes
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain.memory import ConversationBufferMemory
from langchain import hub # Para obtener el prompt base del agente

# --- 2) Definición de la Herramienta (sin cambios) ---
def iniciar_protocolo_interrogatorio(descripcion: str) -> str:
    """Recoge datos básicos para un despido disciplinario. Usar esta herramienta cuando se solicite iniciar un protocolo de despido."""
    preguntas = [
        "¿Cuál es el nombre completo y DNI del trabajador?",
        "¿Cuál es la fecha exacta de los hechos que motivan el despido?",
        "Describe de forma detallada y cronológica cada uno de los hechos imputados.",
        "¿Hay fotografías, vídeos o documentos que prueben esos hechos?",
        "¿Existen testigos? Si es así, proporciona sus nombres y cargos.",
        "¿A qué Convenio Colectivo está sujeto el trabajador?"
    ]
    # Devolvemos las preguntas de una forma clara para el LLM
    return "Protocolo de interrogatorio iniciado. Por favor, haz al usuario las siguientes preguntas una por una:\n" + "\n".join(f"- {p}" for p in preguntas)

# --- 3) Configuración de la Memoria y Herramientas (sin cambios) ---
memory = ConversationBufferMemory(return_messages=True)
tools = [
    Tool(
        name="iniciar_protocolo_interrogatorio",
        func=iniciar_protocolo_interrogatorio,
        description="Recoge datos básicos para un despido disciplinario"
    )
]

# --- 4) Selección de LLM con Modelos de Chat Actuales ---
provider = os.getenv("LLM_PROVIDER", "openai").lower()
if provider == "openai":
    llm = ChatOpenAI(temperature=0)
elif provider == "google":
    # Usamos el modelo Gemini a través de ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0, convert_system_message_to_human=True)
else:
    raise ValueError(f"Proveedor desconocido: {provider}")

# --- 5) Inicialización del Agente con el Método Moderno ---
# Obtenemos un prompt base desde el LangChain Hub
prompt = hub.pull("hwchase17/react-chat")

# Creamos el agente
agent = create_react_agent(llm, tools, prompt)

# Creamos el ejecutor del agente, que es el que realmente corre el bucle
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    memory=memory,
    verbose=True, # Muy útil para ver qué piensa el agente
    max_iterations=10,
    max_execution_time=120
)

# --- 6) Ejecución del Agente ---
def main():
    # Usamos un prompt un poco más claro para el agente
    input_prompt = "Inicia el protocolo para un despido disciplinario"
    print(f"\n=== Ejecutando agente con {provider.upper()}... ===")
    
    # El método moderno es 'invoke' en lugar de 'run'
    resultado = agent_executor.invoke({"input": input_prompt})
    
    print(f"\n=== Resultado Final ===\n")
    # La respuesta está en la clave 'output'
    print(resultado['output'])

if __name__ == "__main__":
    main()
