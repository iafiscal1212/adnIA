import os
import json
from langchain.tools import tool
from dotenv import load_dotenv
import logging
from datetime import datetime

# --- Importaciones Adicionales para la Herramienta Inteligente ---
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()
logging.basicConfig(level=logging.INFO)

# --- PLANTILLAS MAESTRAS DE DOCUMENTOS ---
# Un "arsenal" de plantillas de alta calidad que la herramienta usará.
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

# --- HERRAMIENTA DE REDACCIÓN "SUPERPOTENTE" ---

@tool
def redactor_escritos_juridicos(consulta_detallada: str) -> str:
    """
    Herramienta experta para la redacción final de documentos legales complejos como demandas, contestaciones, contratos o cartas de despido.
    Analiza la petición del usuario, extrae los datos clave y genera un documento completo y profesional.
    Usar esta herramienta como la opción prioritaria para cualquier solicitud de redacción de documentos.
    """
    logging.info("--- Activando Herramienta de Redacción Experta (Doble IA) ---")

    try:
        # --- PASO 1: Clasificación y Extracción de Entidades ---
        classifier_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        json_parser = JsonOutputParser()

        classifier_prompt = PromptTemplate(
            template="""Analiza la siguiente solicitud de un abogado. Tu única tarea es devolver un objeto JSON con dos claves: 'document_type' y 'case_summary'.
            'document_type' debe ser una de las siguientes opciones: [{document_types}].
            'case_summary' debe ser un resumen conciso y claro de los hechos proporcionados por el abogado para incluir en el documento.

            Solicitud:
            {user_query}

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

        # --- PASO 2: Selección de Plantilla ---
        selected_template = DOCUMENT_TEMPLATES[document_type]
        logging.info(f"Tipo de documento identificado: '{document_type}'. Seleccionando plantilla.")

        # --- PASO 3: Redacción y Población por IA ---
        drafter_llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.2)
        
        drafter_prompt = PromptTemplate(
            template="""Eres un Oficial Jurídico experto en la redacción de documentos legales en España.
            Tu única tarea es tomar la plantilla proporcionada y el resumen de los hechos, y generar el texto completo del documento final.
            - Rellena todos los placeholders como [Nombre Cliente] o [Cantidad] con la información del resumen de hechos. Si un dato no está, déjalo como está para que el abogado lo rellene.
            - Expande el resumen de los hechos para crear párrafos coherentes y con terminología jurídica apropiada en la sección 'HECHOS'.
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


# --- HERRAMIENTAS DE APOYO Y CONSULTA ---

@tool
def buscar_en_boe(terminos_de_busqueda: str) -> str:
    """Busca legislación específica (Leyes, Decretos) en el Boletín Oficial del Estado (BOE) cuando se necesite fundamentar un escrito."""
    logging.info(f"--- Usando la herramienta de búsqueda del BOE para: '{terminos_de_busqueda}' ---")
    return f"Resultado simulado de la búsqueda en el BOE para '{terminos_de_busqueda}': Se ha localizado el Real Decreto X/2025 sobre la materia."

@tool
def consultar_jurisprudencia_y_guias_procesales(consulta_especifica: str) -> str:
    """Busca jurisprudencia (sentencias) y guías sobre procedimientos legales para consultas sobre estrategia procesal, plazos o recursos. No usar para redactar."""
    logging.info(f"--- Usando la herramienta de Jurisprudencia para: '{consulta_especifica}' ---")
    return "Análisis de jurisprudencia simulado: La Sentencia del Tribunal Supremo 123/2024 establece que para este tipo de casos, la carga de la prueba recae sobre el demandado."

@tool
def herramienta_experto_derecho_social(consulta_especifica: str) -> str:
    """Herramienta experta para responder preguntas concretas sobre Derecho Social (convenios, cálculos de indemnización, salarios). No usar para redactar documentos completos."""
    logging.info(f"--- Usando la herramienta de consulta de Experto Social ---")
    return "Análisis de Derecho Social: La consulta indica que es necesario revisar el Art. XX del Convenio Colectivo para determinar los plazos de prescripción de la acción."

@tool
def analizador_documental_sherlock(texto_del_documento: str) -> str:
    """Analiza el texto de un documento ya existente para identificar cláusulas clave, riesgos o resumir su contenido."""
    logging.info(f"--- Usando la herramienta 'Sherlock' para analizar un documento ---")
    return "Análisis Preliminar del Documento: Se ha identificado una cláusula de resolución de conflictos que establece la sumisión a los juzgados de Madrid. Alerta: Se ha detectado una cláusula de penalización por desestimiento unilateral del 10% del valor del contrato."
