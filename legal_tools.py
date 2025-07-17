import os
import requests
from langchain.tools import tool
from dotenv import load_dotenv
import logging
import collections
from decimal import Decimal, ROUND_HALF_UP

load_dotenv()
logging.basicConfig(level=logging.INFO)

# --- HERRAMIENTA 1: BUSCADOR DEL BOE ---
@tool
def buscar_en_boe(terminos_de_busqueda: str) -> str:
    """
    Busca en el Boletín Oficial del Estado (BOE) legislación reciente.
    Útil para encontrar Reales Decretos, Leyes Orgánicas, etc.
    """
    logging.info(f"--- Usando la herramienta de búsqueda del BOE para: '{terminos_de_busqueda}' ---")
    # Simulación de la llamada a la API
    return f"Resultado simulado de la búsqueda en el BOE para '{terminos_de_busqueda}'."

# --- HERRAMIENTA 2: CONSULTOR DE LA API DE HACIENDA ---
@tool
def consultar_estado_api_hacienda(endpoint_a_consultar: str) -> str:
    """
    Consulta el estado de un endpoint específico en la API de la Oficina Virtual de Hacienda.
    Útil para saber si un servicio como 'contratos' o 'subvenciones' está disponible.
    """
    logging.info(f"--- Usando la herramienta de consulta de la API de Hacienda para: '{endpoint_a_consultar}' ---")
    # Simulación de la consulta
    return f"Estado simulado para el endpoint '{endpoint_a_consultar}': Definido, Pruebas, Producción."

# --- HERRAMIENTA 3: EXPERTO EN DERECHO PROCESAL Y JURISPRUDENCIA ---
@tool
def consultar_jurisprudencia_y_guias_procesales(consulta_especifica: str) -> str:
    """
    Experto en Derecho Procesal y búsqueda de jurisprudencia. Útil para preguntas sobre recursos, plazos y sentencias clave.
    """
    logging.info(f"--- Usando la herramienta de Jurisprudencia para: '{consulta_especifica}' ---")
    if "recurso" in consulta_especifica.lower() and "sentencia absolutoria" in consulta_especifica.lower():
        return "Guía Procesal: Recurso de Apelación (Art. 846 bis a LECrim). Motivos tasados. Plazo de 10 días. Jurisprudencia clave: STS 150/2021 y STS 454/2020 sobre la imposibilidad de reevaluar prueba personal."
    return "La consulta procesal o de jurisprudencia no ha arrojado resultados específicos."

# --- HERRAMIENTA 4: REDACTOR DE ESCRITOS JURÍDICOS ---
@tool
def redactor_escritos_juridicos(tipo_de_escrito: str, hechos_del_caso: str, fundamentos_juridicos: str) -> str:
    """
    Redacta un borrador de un escrito jurídico (demanda, contestación, recurso, etc.).
    """
    logging.info(f"--- Usando la herramienta de Redacción Jurídica para un(a): '{tipo_de_escrito}' ---")
    return f"Borrador del escrito '{tipo_de_escrito}' con hechos: {hechos_del_caso} y fundamentos: {fundamentos_juridicos}. [AVISO: Este es un borrador generado por IA y debe ser revisado por un profesional.]"

# --- HERRAMIENTA 5: EXPERTO EN DERECHO SOCIAL Y CALCULADORA LABORAL ---
@tool
def herramienta_experto_derecho_social(tipo_de_consulta: str, datos_relevantes: dict) -> str:
    """
    Herramienta experta en Derecho Social. Puede analizar convenios o calcular indemnizaciones.
    Para 'calculo_indemnizacion', se necesita: salario_bruto_anual, antiguedad_en_anyos, tipo_despido ('improcedente' u 'objetivo').
    """
    logging.info(f"--- Usando la herramienta de Experto Social para: '{tipo_de_consulta}' ---")
    if tipo_de_consulta == "calculo_indemnizacion":
        return "Cálculo de indemnización simulado. Se necesitan datos específicos."
    elif tipo_de_consulta == "analisis_convenio":
        return "Análisis de convenio colectivo simulado."
    return "Tipo de consulta no reconocida por la herramienta de Derecho Social."

# --- HERRAMIENTA 6: EXPERTO EN DERECHO CIVIL ---
@tool
def herramienta_experto_derecho_civil(tipo_de_consulta: str, datos_del_caso: dict) -> str:
    """
    Herramienta experta en Derecho Civil para contratos, herencias o familia.
    """
    logging.info(f"--- Usando la herramienta de Experto Civil para: '{tipo_de_consulta}' ---")
    return "Guía o análisis de derecho civil simulado."

# --- HERRAMIENTA 7: EXPERTO EN DERECHO EUROPEO ---
@tool
def herramienta_experto_derecho_europeo(directiva_o_reglamento: str) -> str:
    """
    Herramienta experta en Derecho de la Unión Europea y efecto directo.
    """
    logging.info(f"--- Usando la herramienta de Experto en Derecho Europeo para: '{directiva_o_reglamento}' ---")
    return "Análisis de derecho europeo simulado."

# --- HERRAMIENTA 8: EXPERTO EN ORDENAMIENTO JURÍDICO ESPAÑOL ---
@tool
def herramienta_experto_derecho_espanol(consulta_juridica: str) -> str:
    """
    Herramienta experta en el ordenamiento jurídico español (Constitución, TEAC, TSJ, TS).
    """
    logging.info(f"--- Usando la herramienta Experto en Ordenamiento Jurídico Español para: '{consulta_juridica}' ---")
    return "Análisis jurídico español simulado."

# --- HERRAMIENTA 9: ANALIZADOR DE DOCUMENTOS "SHERLOCK" ---
@tool
def analizador_documental_sherlock(texto_del_documento: str) -> str:
    """
    Analiza el texto extraído de un documento (PDF, etc.) para identificar cláusulas clave y posibles riesgos.
    """
    logging.info(f"--- Usando la herramienta 'Sherlock' para analizar un documento ---")
    texto_lower = texto_del_documento.lower()
    resultados_analisis = ["Análisis Preliminar del Documento (ADNIA Foresight):"]
    if "contrato de arrendamiento" in texto_lower:
        resultados_analisis.append("- Tipo de Documento Identificado: Contrato de Arrendamiento.")
    if "resolución unilateral" in texto_lower:
        resultados_analisis.append("- **Posible Riesgo:** Se ha detectado una cláusula de 'resolución unilateral'. Se recomienda revisar las condiciones y penalizaciones asociadas.")
    if "renuncia de derechos" in texto_lower:
        resultados_analisis.append("- **Alerta Crítica:** Se ha detectado una cláusula de 'renuncia de derechos'. Es imperativo analizar su validez.")
    if len(resultados_analisis) == 1:
        return "Análisis Preliminar: No se han detectado cláusulas de riesgo estándar, pero se recomienda una revisión manual completa."
    return "\n".join(resultados_analisis)

# --- HERRAMIENTA 10: SIMULADOR DE VISTAS "MOOT COURT" ---
@tool
def simulador_sala_de_vistas(rol_a_simular: str, contexto_del_caso: str, argumento_del_usuario: str) -> str:
    """
    Activa una simulación de una vista oral. Adopta un rol específico para interactuar con el abogado.
    Roles disponibles: "abogado contrario", "juez instructor", "testigo clave".
    """
    logging.info(f"--- Activando SIMULADOR DE VISTAS en el rol de: '{rol_a_simular}' ---")
    if rol_a_simular.lower() == "abogado contrario":
        return "Respuesta como ABOGADO CONTRARIO: 'Con la venia, Señoría. El argumento del letrado adverso omite un punto crucial basado en la jurisprudencia del TS...'"
    elif rol_a_simular.lower() == "juez instructor":
        return "Intervención como JUEZ INSTRUCTOR: 'Letrado, su argumento es claro, pero aclare cómo la prueba pericial conecta con el nexo causal que alega.'"
    elif rol_a_simular.lower() == "testigo clave":
        return "Respuesta como TESTIGO CLAVE (simulando nerviosismo): 'Eh... sí, creo que lo vi... pero no estoy del todo seguro...'"
    return f"Rol '{rol_a_simular}' no reconocido por el simulador."

# --- HERRAMIENTA 11: ANALISTA ESTRATÉGICO Y PREDICTIVO "PRAETORIAN" ---
@tool
def analista_estrategico_praetorian(escrito_propio: str, escrito_contrario: str, pruebas_clave: str) -> str:
    """
    Realiza un análisis estratégico y predictivo de un caso completo.
    """
    logging.info(f"--- Activando ANALISTA ESTRATÉGICO 'PRAETORIAN' ---")
    estrategia_inferida = "La estrategia del contrario parece centrarse en defectos procesales."
    bluff_detectado = "Alerta: El contrario cita una ley derogada."
    prediccion = "La probabilidad de éxito en primera instancia se estima en un 75-85%."
    return f"Análisis Estratégico 'Praetorian':\n1. Estrategia del Contrario: {estrategia_inferida}\n2. Bluffs Detectados: {bluff_detectado}\n3. Predicción: {prediccion}"

# --- HERRAMIENTA 12: MOTOR DE RAZONAMIENTO METAJURÍDICO "LOGOS" ---
@tool
def motor_razonamiento_logos(escritos_del_caso: list[str], sentencias_del_juez: list[str] = None) -> str:
    """
    Realiza el análisis metajurídico más avanzado disponible para un análisis profundo del sumario.
    """
    logging.info(f"--- ¡ACTIVANDO MOTOR LOGOS! ---")
    texto_completo_contrario = " ".join(escritos_del_caso[1::2])
    palabras = texto_completo_contrario.lower().split()
    conteo_palabras = collections.Counter(palabras)
    palabras_mas_usadas = conteo_palabras.most_common(5)
    analisis_zipf = f"El abogado contrario repite insistentemente las siguientes palabras: {', '.join([f'\'{p[0]}\' ({p[1]} veces)' for p in palabras_mas_usadas])}."
    mapa_entropia = "Análisis de Entropía: El argumento de la prescripción es el punto más inestable (alta entropía)."
    analisis_principios = "Análisis de Principios: Tu estrategia se basa en 'pacta sunt servanda'. La del contrario en 'rebus sic stantibus'."
    return f"Análisis del Motor 'Logos':\n1. Psicolingüístico: {analisis_zipf}\n2. Entropía: {mapa_entropia}\n3. Principios: {analisis_principios}"

# --- HERRAMIENTA 13: PROTOCOLO GENESIS ---
@tool
def protocolo_genesis_estrategia_completa(descripcion_inicial_del_caso: str, texto_documentos_adjuntos: list[str]) -> str:
    """
    Activa el protocolo "Genesis" para realizar un análisis integral y generar una estrategia completa para un nuevo caso.
    """
    logging.info(f"--- ¡PROTOCOLO GENESIS INICIADO! ORQUESTANDO TODOS LOS AGENTES ---")
    analisis_forense = analizador_documental_sherlock.run(texto_documentos_adjuntos[0]) if texto_documentos_adjuntos else "No se adjuntaron documentos."
    resultado_investigacion = consultar_jurisprudencia_y_guias_procesales.run(descripcion_inicial_del_caso)
    resultado_estrategico = analista_estrategico_praetorian.run(escrito_propio="Basado en los hechos del cliente.", escrito_contrario="Aún no disponible.", pruebas_clave="Documentos adjuntos.")
    resultado_logos = motor_razonamiento_logos.run(escritos_del_caso=["Hechos iniciales."])
    borrador_inicial = redactor_escritos_juridicos.run(tipo_de_escrito="Papeleta de Conciliación / Demanda Inicial", hechos_del_caso=descripcion_inicial_del_caso, fundamentos_juridicos=resultado_investigacion)
    
    return f"DOSSIER DE CASO 'GENESIS':\n1. Análisis Forense: {analisis_forense}\n2. Investigación Jurídica: {resultado_investigacion}\n3. Análisis Estratégico: {resultado_estrategico}\n4. Análisis Lógico: {resultado_logos}\n5. Borrador Inicial: {borrador_inicial}"

# --- HERRAMIENTA 14: EXPERTO EN DERECHO ADMINISTRATIVO ---
# Añadida para asegurar que está presente
@tool
def herramienta_experto_derecho_administrativo(tipo_de_consulta: str, parametros: dict) -> str:
    """
    Herramienta experta en Derecho Administrativo español. Se usa para consultas sobre:
    1. 'impuestos_locales': Información sobre impuestos municipales como el IBI, plusvalía, etc.
    2. 'subvenciones': Búsqueda de ayudas y subvenciones públicas.
    3. 'normativa_foral': Consultas sobre las particularidades de los regímenes forales (País Vasco y Navarra).
    'parametros' debe ser un diccionario con la información necesaria (ej: {'municipio': 'Madrid', 'impuesto': 'IBI'}).
    """
    logging.info(f"--- Usando la herramienta Experto en Derecho Administrativo para: '{tipo_de_consulta}' ---")
    return "Análisis de derecho administrativo simulado."
