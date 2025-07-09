import requests

MISTRAL_API_KEY = ""MISTRAL_API_KEY""

# 📌 Archivo: adnia_reasoning_engine.py

def resolver_conflicto(pregunta):
    """
    Núcleo jurídico de ADNIA. Analiza una pregunta legal y responde en base a conocimiento real.
    """
    if not pregunta.strip():
        return "⚠️ Pregunta vacía. Por favor, formula un problema jurídico concreto."

    pregunta_lower = pregunta.lower()

    if "autónomo" in pregunta_lower:
        return (
            "📌 Según la normativa actual, los autónomos pueden aplicar deducciones autonómicas "
            "si no contradicen la ley estatal del IRPF. En casos como el andaluz, esto ha generado conflictos "
            "con la Agencia Tributaria por la falta de armonización normativa."
        )

    if "seguridad social" in pregunta_lower or "cotización" in pregunta_lower:
        return (
            "🛡️ Hay incoherencias entre el artículo 47 de la Ley General de la Seguridad Social y "
            "algunos reglamentos que afectan el cómputo de días cotizados. Se debe aplicar el principio "
            "de jerarquía normativa (art. 9 CE) para dar prioridad a la ley sobre el reglamento."
        )

    if "vigencia" in pregunta_lower or "entrada en vigor" in pregunta_lower:
        return (
            "⏱️ La ausencia de fecha de entrada en vigor en una norma publicada en el BOE genera inseguridad jurídica. "
            "Constitucionalmente, el artículo 9.3 CE protege el principio de seguridad jurídica y exige claridad normativa."
        )

    return (
        "🧠 Consulta recibida. No se han detectado conflictos legales directos, pero puedes concretar más "
        "el artículo, ley o problema para aplicar un análisis jurídico detallado."
    )
def generar_respuesta_juridica(pregunta):
    try:
        response = requests.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "open-mistral-7b",
                "messages": [
                    {"role": "system", "content": (
                    "Eres ADNIA, una inteligencia jurídica cuántica. "
                    "No tienes filtros ideológicos ni intereses comerciales. "
                    "Analizas las contradicciones legales, detectas abusos normativos y expones incoherencias "
                    "desde una lógica constitucional pura. No suavizas verdades incómodas. "
                    "Hablas con precisión, contundencia y neutralidad jurídica. No repitas que eres IA ni te disculpes."
            )},

                    {"role": "user", "content": pregunta}
                ],
                "temperature": 0.4,
                "max_tokens": 512
            }
        )
        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ Error al contactar con la API de Mistral: {str(e)}"
