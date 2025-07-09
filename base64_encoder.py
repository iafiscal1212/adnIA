
import base64
import sys

def convertir_a_base64(ruta_archivo):
    try:
        with open(ruta_archivo, "rb") as archivo:
            codificado = base64.b64encode(archivo.read()).decode("utf-8")
            print(f"\n✅ Archivo convertido a Base64:\n\n{codificado}\n")
            return codificado
    except Exception as e:
        print(f"⚠️ Error al convertir archivo: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python base64_encoder.py ruta/del/archivo.ext")
    else:
        convertir_a_base64(sys.argv[1])
