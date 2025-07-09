# copiloto_codigo.py
import os
import time
import pyttsx3

# Rutas de archivos a vigilar
RUTAS_VIGILADAS = ["./"]  # Directorios donde trabajas en tu código

# Extensiones de archivo que queremos observar
EXTENSIONES_OBJETIVO = [".py", ".js", ".html", ".jsx"]

# Frases clave para detectar
PATRONES_CRITICOS = [
    ("input(", "Entrada insegura detectada: input() sin validación"),
    ("eval(", "Uso de eval() detectado: posible vulnerabilidad"),
    ("open(", "Apertura de archivo: comprueba permisos y RGPD"),
    ("SELECT", "Consulta SQL detectada: evalúa sanitización"),
    ("fetch(", "Llamada a API: revisa si tiene datos sensibles"),
    ("bcrypt", "Se detecta cifrado: ¿cumple normativa de protección de datos?"),
    ("localStorage", "Uso de localStorage: cuidado con datos personales"),
]

voz = pyttsx3.init()
voz.setProperty("rate", 160)
voz.setProperty("volume", 1.0)

def hablar(texto):
    print(f"[ADNIA-CÓDIGO] {texto}")
    voz.say(texto)
    voz.runAndWait()

def analizar_linea(linea):
    for patron, alerta in PATRONES_CRITICOS:
        if patron in linea:
            hablar(alerta)

def escanear_archivos():
    print("👁️ ADNIA Copiloto de Código activo...")
    archivos_vistos = {}

    while True:
        for carpeta in RUTAS_VIGILADAS:
            for root, _, archivos in os.walk(carpeta):
                for archivo in archivos:
                    if any(archivo.endswith(ext) for ext in EXTENSIONES_OBJETIVO):
                        ruta = os.path.join(root, archivo)
                        try:
                            mod_time = os.path.getmtime(ruta)
                            if ruta not in archivos_vistos or archivos_vistos[ruta] < mod_time:
                                archivos_vistos[ruta] = mod_time
                                with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                                    lineas = f.readlines()
                                    for linea in lineas:
                                        analizar_linea(linea)
                        except Exception as e:
                            print(f"Error leyendo {ruta}: {e}")
        time.sleep(5)

def iniciar_copiloto_codigo():
    escanear_archivos()
