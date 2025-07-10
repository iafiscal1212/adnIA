# humanshield_module_adnia.py
# Módulo de "HumanShield" para integrar en AdnIA con API de Humbot
# Automatiza el proceso de humanización de textos jurídicos IA

import requests
import datetime
import os

# Configurable por variable de entorno para seguridad
def get_api_key():
    return os.getenv("HUMBOT_API_KEY")


def humanize_with_humbot(text, language="es", creativity="medium", mode="standard"):
    url = "https://api.humbot.ai/v1/humanizer"
    api_key = get_api_key()
    if not api_key:
        raise ValueError("Falta la clave API de Humbot. Configura la variable de entorno 'HUMBOT_API_KEY'.")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "text": text,
        "humanize_mode": mode,
        "creativity_level": creativity,
        "language": language
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return {
            "original": text,
            "humanized": result.get("humanized_text", ""),
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    except requests.exceptions.HTTPError as err:
        return {"error": f"Error HTTP: {err}"}
    except Exception as e:
        return {"error": str(e)}


# Ejemplo de uso para integración en AdnIA:
if __name__ == "__main__":
    sample_text = """
    Por consiguiente, el demandante solicita la nulidad de la cláusula. Es importante señalar que la jurisprudencia ha avalado esta interpretación. Además, se adjuntan pruebas documentales. Por lo tanto, se ruega admitir el escrito.
    """

    os.environ["HUMBOT_API_KEY"] = "TU_API_KEY_AQUI"  # Solo para prueba local

    resultado = humanize_with_humbot(sample_text)
    if "error" in resultado:
        print("[ERROR]", resultado["error"])
    else:
        print("Texto original:\n", resultado["original"])
        print("\nTexto humanizado:\n", resultado["humanized"])
        print("\nGenerado el:", resultado["timestamp"])
