# 📌 Archivo: adnia_alertas_legales.py

import json

def cargar_trampas_legales():
    try:
        with open("trampas_legales.json", "r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
            return datos
    except Exception as e:
        print(f"⚠️ Error al cargar trampas_legales.json: {e}")
        return []

def generar_alertas():
    trampas = cargar_trampas_legales()
    alertas = []

    for trampa in trampas:
        alerta = {
            "titular": trampa.get("titular", "Conflicto sin titular"),
            "trampa": trampa.get("descripcion", "Descripción no disponible")
        }

        # Si incluye datos constitucionales conflictivos:
        if "constitucion" in trampa:
            alerta["constitucion"] = {
                "articulo": trampa["constitucion"].get("articulo"),
                "titulo": trampa["constitucion"].get("titulo"),
                "texto": trampa["constitucion"].get("texto")
            }

        alertas.append(alerta)

    return alertas

# Si ejecutas este archivo directamente:
if __name__ == "__main__":
    print("🔎 Generando alertas legales desde trampas_legales.json...\n")
    alertas = generar_alertas()
    for alerta in alertas:
        print(json.dumps(alerta, indent=2, ensure_ascii=False))
