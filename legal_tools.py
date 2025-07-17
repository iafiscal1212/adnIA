import os
import json
from langchain.tools import tool
from dotenv import load_dotenv
import logging
from datetime import datetime

# --- Importaciones Adicionales para la Herramienta Inteligente y RAG ---
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()
logging.basicConfig(level=logging.INFO)

# --- PLANTILLAS MAESTRAS DE DOCUMENTOS ---
DOCUMENT_TEMPLATES = {
    "carta_despido": """
[Ciudad], a {fecha}

[DATOS DE LA EMPRESA]
[Dirección]

A la atención de:
D./Dña. [Nombre del Trabajador]
[Dirección del Trabajador]

ASUNTO: CARTA DE DESPIDO DISCIPLINARIO

Estimado/a señor/a,
Por medio de la presente, la Dirección de esta empresa le notifica la decisión de extinguir la relación laboral que nos une con fecha de efectos del día de hoy, mediante despido disciplinario, en base a los incumplimientos contractuales graves y culpables que se detallan a continuación.

HECHOS:
{hechos_del_caso}

FUNDAMENTOS DE DERECHO:
I.- El contrato de trabajo podrá extinguirse por decisión del empresario, mediante despido basado en un incumplimiento grave y culpable del trabajador, de conformidad con el Artículo 54.1 del Real Decreto Legislativo 2/2015, de 23 de octubre, por el que se aprueba el texto refundido de la Ley del Estatuto de los Trabajadores.
II.- Específicamente, los hechos descritos constituyen una transgresión de la buena fe contractual y un abuso de confianza en el desempeño del trabajo, según el Art. 54.2.d) del citado texto legal.
III.- Asimismo, resultan de aplicación los artículos pertinentes del Convenio Colectivo de [Convenio Aplicable] en materia de régimen disciplinario.

Por todo lo expuesto, le comunicamos la extinción de su relación laboral. La liquidación, saldo y finiquito correspondientes se encuentran a su disposición en las oficinas de la empresa.
Rogamos firme el recibí de esta comunicación, a los meros efectos de notificación.

Atentamente,
Fdo.: La Dirección de la Empresa.
""",
    "demanda_juicio_ordinario": """
AL JUZGADO DE PRIMERA INSTANCIA DE [Lugar del Juzgado] QUE POR TURNO CORRESPONDA

D./Dña. [Nombre Procurador], Procurador/a de los Tribunales, en nombre y representación de D./Dña. [Nombre Cliente], mayor de edad, con domicilio en [Dirección Cliente] y D.N.I. [DNI Cliente], representación que acredito mediante [Poder General para Pleitos / Apud Acta], y bajo la dirección letrada de D./Dña. [Nombre Abogado], colegiado/a n.º [Número Colegiado] del Ilustre Colegio de Abogados de [Colegio Abogados], ante el Juzgado comparezco y como mejor proceda en Derecho, DIGO:

Que por medio del presente escrito formulo DEMANDA DE JUICIO ORDINARIO en reclamación de [Objeto de la Demanda] contra D./Dña. [Nombre Demandado], con domicilio en [Dirección Demandado], en base a los siguientes

HECHOS:
{hechos_del_caso}

FUNDAMENTOS DE DERECHO:
(Fundamentos de derecho procesal y sustantivo a desarrollar por la IA)

Por todo lo expuesto,

SUPLICO AL JUZGADO: Que tenga por presentado este escrito de demanda junto con sus documentos, lo admita a trámite y, previos los trámites legales oportunos, dicte Sentencia por la que se estime íntegramente la presente demanda, y en consecuencia, se condene a la parte demandada a [Petición Concreta], con expresa imposición de costas.

En [Lugar], a {fecha}.

Fdo.: [Nombre Abogado]      Fdo.: [Nombre Procurador]
""",
    "contrato_arrendamiento": """
CONTRATO DE ARRENDAMIENTO DE VIVIENDA

En [Lugar], a {fecha}

REUNIDOS
De una parte, D./Dña. [Nombre Arrendador], en adelante "EL ARRENDADOR".
De otra parte, D./Dña. [Nombre Arrendatario], en adelante "EL ARRENDATARIO".

Ambas partes se reconocen mutua capacidad legal para celebrar el presente CONTRATO DE ARRENDAMIENTO DE VIVIENDA, y a tal efecto,

EXPONEN Y PACTAN
{hechos_del_caso}

(Cláusulas sobre duración, renta, fianza, obligaciones, etc., a desarrollar por la IA)

Y en prueba de conformidad, las partes firman el presente contrato por duplicado en el lugar y fecha arriba indicados.

EL ARRENDADOR               EL ARRENDATARIO
Fdo.: [Nombre Arrendador]    Fdo.: [Nombre Arrendatario]
"""
}

QUESTIONS_BANK = {
    "carta_despido": [
        "¿Cuál es el nombre completo y DNI del trabajador?",
        "¿Cuál es la fecha exacta de los hechos que motivan el despido?",
        "Describe de forma detallada y cronológica cada uno de los hechos imputados.",
        "¿Existen pruebas directas (documentos, fotos, vídeos)? ¿Cuáles son?",
        "¿Hay testigos de los hechos? Si es así, proporciona sus nombres y cargos.",
        "¿A qué Convenio Colectivo está sujeto el trabajador?"
    ],
    "demanda_juicio_ordinario": [
        "¿Quién es el demandante (nombre completo, DNI, domicilio)?",
        "¿Quién es el demandado (nombre completo, DNI, domicilio)?",
        "¿Cuál es la cantidad exacta que se reclama?",
        "Describe cronológicamente los hechos que dan lugar a la reclamación.",
        "¿Qué documentos (contratos, facturas, burofaxes) sustentan la reclamación?"
    ],
    "contrato_arrendamiento": [
        "¿Quién es el arrendador (propietario)?",
        "¿Quién es el arrendatario (inquilino)?",
        "¿Cuál es la dirección exacta de la vivienda a arrendar?",
        "¿Cuál será el importe de la renta mensual en euros?",
        "¿Cuál será la duración inicial del contrato en años?",
        "¿Qué día del mes se deberá abonar la renta?"
    ]
}


# --- HERRAMIENTAS PRINCIPALES DE PROTOCOLO Y REDACCIÓN ---

@tool
def consultar_base_de_conocimiento(pregunta_especifica: str) -> str:
    """
    USAR ESTA HERRAMIENTA SÓLO para buscar información legal, artículos o fundamentos de derecho en la base de datos jurídica interna.
    Es ideal para responder preguntas como '¿Qué dice el Estatuto de los Trabajadores sobre el despido?' o para encontrar la base legal para un caso.
    NO USAR para redactar un documento completo.
    """
    logging.info(f"--- Consultando la base de conocimiento (RAG) para: '{pregunta_especifica}' ---")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        retriever = db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
        docs = retriever.invoke(pregunta_especifica)
        if not docs: return "No se encontró información relevante en la base de datos."
        contexto = "\n---\n".join([doc.page_content for doc in docs])
        return f"Información relevante encontrada en la base de datos:\n{contexto}"
    except Exception as e:
        logging.error(f"Error al consultar la base de datos vectorial: {e}")
        return "Error al acceder a la base de conocimiento. La carpeta 'faiss_index' podría no existir. Ejecute primero el script 'ingest.py'."

@tool
def iniciar_protocolo_interrogatorio(tipo_de_documento: str) -> str:
    """
    USAR ESTA HERRAMIENTA PRIMERO y solo una vez al inicio de una solicitud de redacción para obtener la lista de preguntas necesarias.
    El input es el tipo de documento a redactar (ej: 'carta_despido').
    NO USAR si ya se está en medio de una conversación o interrogatorio.
    """
    logging.info(f"--- Iniciando protocolo de interrogatorio para: {tipo_de_documento} ---")
    document_type_key = tipo_de_documento.lower()
    if "demanda" in document_type_key: document_type_key = "demanda_juicio_ordinario"
    elif "contrato" in document_type_key: document_type_key = "contrato_arrendamiento"
    elif "despido" in document_type_key: document_type_key = "carta_despido"
    questions = QUESTIONS_BANK.get(document_type_key)
    if not questions: return "Error: No se encontró un protocolo de interrogatorio para el tipo de documento especificado."
    return json.dumps(questions)

@tool
def preguntar_al_usuario(pregunta: str) -> str:
    """
    Usa esta herramienta DESPUÉS de obtener la lista de preguntas con 'iniciar_protocolo_interrogatorio', para hacer cada pregunta individualmente al usuario.
    El input es la pregunta exacta que quieres hacer.
    NO USAR para responder a la pregunta inicial del usuario.
    """
    logging.info(f"--- Usando la herramienta para preguntar al usuario: {pregunta} ---")
    return pregunta

@tool
def redactor_escritos_juridicos(consulta_detallada: str) -> str:
    """
    Herramienta experta para la REDACCIÓN FINAL de un documento legal.
    USAR ESTA HERRAMIENTA SÓLO DESPUÉS de haber recopilado toda la información necesaria del usuario.
    El input debe ser un resumen completo con todos los datos del caso.
    """
    logging.info("--- Activando Herramienta de Redacción Experta v2 (con Fundamentos Dinámicos) ---")
    try:
        classifier_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        json_parser = JsonOutputParser()
        classifier_prompt = PromptTemplate(
            template="""Analiza la siguiente solicitud de un abogado. Tu única tarea es devolver un objeto JSON con dos claves: 'document_type' y 'case_summary'.
            'document_type' debe ser una de las siguientes opciones: [{document_types}].
            'case_summary' debe ser un resumen conciso y claro de los hechos proporcionados por el abogado para incluir en el documento.
            Solicitud: {user_query}
            {format_instructions}""",
            input_variables=["user_query", "document_types"],
            partial_variables={"format_instructions": json_parser.get_format_instructions()},
        )
        classifier_chain = classifier_prompt | classifier_llm | json_parser
        classification_result = classifier_chain.invoke({
            "user_query": consulta_detallada,
            "document_types": ", ".join(DOCUMENT_TEMPLATES.keys())
        })
        document_type = classification_result.get("document_type")
        case_summary = classification_result.get("case_summary")
        if not document_type or document_type not in DOCUMENT_TEMPLATES:
            return f"Error: No se pudo determinar el tipo de documento o no existe una plantilla para '{document_type}'."
        selected_template = DOCUMENT_TEMPLATES[document_type]
        logging.info(f"Tipo de documento identificado: '{document_type}'. Seleccionando plantilla.")
        drafter_llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
        drafter_prompt = PromptTemplate(
            template="""Eres un Oficial Jurídico experto en la redacción de documentos legales en España.
            Tu única tarea es tomar la plantilla proporcionada y el resumen de los hechos, y generar el texto completo del documento final.
            - Expande el resumen de los hechos para crear párrafos coherentes y con terminología jurídica apropiada en la sección 'HECHOS'.
            - IMPORTANTE: Si en la plantilla encuentras el texto '(Fundamentos de derecho procesal y sustantivo a desarrollar por la IA)', DEBES reemplazarlo por una argumentación jurídica completa y detallada, basada en los hechos del caso y citando la legislación española aplicable.
            - No añadas comentarios, avisos ni texto que no pertenezca al documento legal. Tu output debe ser únicamente el texto del documento.

            PLANTILLA:
            {template}

            RESUMEN DE HECHOS DEL CASO:
            {summary}

            DOCUMENTO FINAL COMPLETO:
            """,
            input_variables=["template", "summary"]
        )
        drafter_chain = drafter_prompt | drafter_llm
        final_document = drafter_chain.invoke({
            "template": selected_template.format(fecha=datetime.now().strftime('%d de %B de %Y'), hechos_del_caso=case_summary),
            "summary": case_summary
        }).content
        return final_document
    except Exception as e:
        logging.error(f"Error en la herramienta de redacción experta: {e}")
        return "Se ha producido un error interno al generar el documento. Por favor, revise la petición o inténtelo de nuevo."

# --- HERRAMIENTAS DE APOYO Y CONSULTA (con descripciones mejoradas) ---

@tool
def buscar_en_boe(terminos_de_busqueda: str) -> str:
    """USAR SÓLO para buscar Leyes, Decretos o normativa específica en el Boletín Oficial del Estado. NO USAR para redactar ni para buscar jurisprudencia."""
    logging.info(f"--- Usando la herramienta de búsqueda del BOE para: '{terminos_de_busqueda}' ---")
    return f"Resultado simulado de la búsqueda en el BOE para '{terminos_de_busqueda}': Se ha localizado el Real Decreto X/2025 sobre la materia."

@tool
def consultar_estado_api_hacienda(endpoint_a_consultar: str) -> str:
    """USAR SÓLO para consultar el estado de un servicio (endpoint) específico de la API de Hacienda."""
    logging.info(f"--- Usando la herramienta de consulta de la API de Hacienda para: '{endpoint_a_consultar}' ---")
    return f"Estado simulado para el endpoint '{endpoint_a_consultar}': Definido, Pruebas, Producción."

@tool
def consultar_jurisprudencia_y_guias_procesales(consulta_especifica: str) -> str:
    """USAR SÓLO para buscar sentencias (jurisprudencia) o guías sobre procedimientos, plazos y recursos. NO USAR para redactar documentos."""
    logging.info(f"--- Usando la herramienta de Jurisprudencia para: '{consulta_especifica}' ---")
    return "Análisis de jurisprudencia simulado: La Sentencia del Tribunal Supremo 123/2024 establece que para este tipo de casos, la carga de la prueba recae sobre el demandado."

@tool
def herramienta_experto_derecho_social(pregunta_concreta: str) -> str:
    """USAR SÓLO para responder preguntas teóricas o específicas sobre Derecho Social (convenios, cálculos, salarios). NO USAR para redactar."""
    logging.info(f"--- Usando la herramienta de consulta de Experto Social ---")
    return "Análisis de Derecho Social: La consulta indica que es necesario revisar el Art. XX del Convenio Colectivo para determinar los plazos de prescripción de la acción."

@tool
def herramienta_experto_derecho_civil(consulta_civil_detallada: str) -> str:
    """USAR SÓLO para responder preguntas teóricas o específicas sobre Derecho Civil (contratos, herencias, familia). NO USAR para redactar."""
    logging.info(f"--- Usando la herramienta de Experto Civil para: '{consulta_civil_detallada[:50]}...' ---")
    return "Guía o análisis de derecho civil simulado."

@tool
def herramienta_experto_derecho_europeo(consulta_europea_detallada: str) -> str:
    """USAR SÓLO para responder preguntas teóricas o específicas sobre Derecho de la UE. NO USAR para redactar."""
    logging.info(f"--- Usando la herramienta de Experto en Derecho Europeo para: '{consulta_europea_detallada[:50]}...' ---")
    return "Análisis de derecho europeo simulado."

@tool
def herramienta_experto_derecho_espanol(consulta_juridica: str) -> str:
    """USAR SÓLO para responder preguntas teóricas o específicas sobre el ordenamiento jurídico español. NO USAR para redactar."""
    logging.info(f"--- Usando la herramienta Experto en Ordenamiento Jurídico Español para: '{consulta_juridica[:50]}...' ---")
    return "Análisis jurídico español simulado."

@tool
def herramienta_experto_derecho_administrativo(consulta_administrativa_detallada: str) -> str:
    """USAR SÓLO para responder preguntas teóricas o específicas sobre Derecho Administrativo (impuestos, subvenciones). NO USAR para redactar."""
    logging.info(f"--- Usando la herramienta Experto en Derecho Administrativo ---")
    return "Análisis de derecho administrativo simulado."

@tool
def analizador_documental_sherlock(texto_del_documento: str) -> str:
    """USAR SÓLO para analizar o resumir el contenido de un documento que el usuario ya ha proporcionado. NO USAR para redactar un documento nuevo."""
    logging.info(f"--- Usando la herramienta 'Sherlock' para analizar un documento ---")
    return "Análisis Preliminar del Documento: Se ha identificado una cláusula de resolución de conflictos que establece la sumisión a los juzgados de Madrid."

@tool
def simulador_sala_de_vistas(simulacion_detallada: str) -> str:
    """USAR SÓLO para simular una vista oral o un interrogatorio, adoptando un rol (juez, abogado contrario). El input debe describir el escenario."""
    logging.info(f"--- Activando SIMULADOR DE VISTAS ---")
    return f"Respuesta de simulación: 'Señor letrado, proceda a exponer sus conclusiones sobre la falta de prueba que alega.'"

@tool
def analista_estrategico_praetorian(resumen_del_caso: str) -> str:
    """USAR SÓLO para realizar un análisis estratégico y predictivo de un caso. El input debe ser un resumen del caso."""
    logging.info(f"--- Activando ANALISTA ESTRATÉGICO 'PRAETORIAN' ---")
    return "Análisis Estratégico 'Praetorian': La estrategia del contrario parece centrarse en defectos procesales. La probabilidad de éxito se estima en un 75-85%."

@tool
def motor_razonamiento_logos(sumario_del_caso: str) -> str:
    """USAR SÓLO para realizar un análisis metajurídico profundo de un caso. El input debe ser un resumen del sumario del caso."""
    logging.info(f"--- ¡ACTIVANDO MOTOR LOGOS! ---")
    return "Análisis del Motor 'Logos': El punto más débil del caso es el argumento de la prescripción (alta entropía)."

@tool
def protocolo_genesis_estrategia_completa(descripcion_completa_del_caso: str) -> str:
    """USAR SÓLO para activar un protocolo de análisis integral y generar una estrategia completa para un nuevo caso desde cero."""
    logging.info(f"--- ¡PROTOCOLO GENESIS INICIADO! ---")
    return "DOSSIER DE CASO 'GENESIS' generado con éxito."
