import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime

def escanear_boe():
    url = "https://www.boe.es/diario_boe/xml.php?id=BOE-S-2025-05-06"
    respuesta = requests.get(url)

    if respuesta.status_code == 200:
        tree = ET.fromstring(respuesta.content)
        titulares = []

        for dispo in tree.findall(".//disposicion"):
            titulo = dispo.find("titulo")
            if titulo is not None:
                titulares.append(titulo.text.strip())

        ultimos = titulares[:5]
        guardar_en_memoria(ultimos)

        print("\n✅ BOE escaneado. Titulares extraídos:\n")
        for i, t in enumerate(ultimos, 1):
            print(f"{i}. {t}")

    else:
        print("⚠️ Error accediendo al BOE XML.")

def guardar_en_memoria(titulares):
    try:
        with open("adnia_memory.json", "r", encoding="utf-8") as archivo:
            memoria = json.load(archivo)
    except FileNotFoundError:
        memoria = {
            "boe_alertas": [],
            "conceptos_aprendidos": [],
            "registro_general": []
        }

    memoria["boe_alertas"].append({
        "fecha": datetime.now().isoformat(),
        "titulares": titulares
    })

    with open("adnia_memory.json", "w", encoding="utf-8") as archivo:
        json.dump(memoria, archivo, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    
 def escanear_boe():
    hoy = datetime.datetime.now().strftime("%Y-%m-%d")
    url = f"https://www.boe.es/diario_boe/xml.php?id=BOE-S-{hoy}"
    headers = {"User-Agent": "Mozilla/5.0"}
    respuesta = requests.get(url, headers=headers)

    if respuesta.status_code == 200 and "xml" in respuesta.headers.get("Content-Type", "").lower():
        try:
            tree = ET.fromstring(respuesta.content)
            titulares = [
                d.find("titulo").text.strip()
                for d in tree.findall(".//disposicion")
                if d.find("titulo") is not None
            ][:5]

            guardar_en_memoria(titulares)

            print("\n✅ BOE escaneado. Titulares extraídos:\n")
            for i, t in enumerate(titulares, 1):
                print(f"{i}. {t}")
        except ET.ParseError:
            print("⚠️ El contenido recibido no es XML válido.")
    else:
        print("⚠️ No se pudo acceder al XML del BOE de hoy.")

