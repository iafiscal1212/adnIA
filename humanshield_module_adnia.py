# humanshield_module_adnia.py (MEJORADO CON FALLBACK - JULIO 2025)

import requests
import datetime
import os

def get_api_key():
    return os.getenv("HUMBOT_API_KEY")

def humanize_with_humbot(text, language="es", creativity="medium", mode="standard"):
    url = "https://api.humbot.ai/v1/humanizer"
    api_key = get_api_key()
    if not api_key:
        print("Advertencia: No API key; usando fallback.")
        return {"humanized": text}  # Fallback: Retorna original

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    payload = {"text": text, "humanize_mode": mode, "creativity_level": creativity, "language": language}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)  # NUEVO: Timeout
        response.raise_for_status()
        result = response.json()
        return {"original": text, "humanized": result.get("humanized_text", text), "timestamp": datetime.datetime.utcnow().isoformat()}
    except Exception as e:
        print(f"Error en Humbot API: {e}; usando fallback.")
        return {"humanized": text}  # Fallback si falla

if __name__ == "__main__":
    sample_text = "Ejemplo de texto."
    os.environ["HUMBOT_API_KEY"] = "TU_API_KEY_AQUI"  # Prueba local
    resultado = humanize_with_humbot(sample_text)
    print(resultado)
