# copiloto_visual.py
import pytesseract
import pyttsx3
import time
from PIL import ImageGrab
import os

# Configuración de OCR y Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"

# Configuración de voz
voz = pyttsx3.init()
voz.setProperty('rate', 160)  # velocidad normal
voz.setProperty('volume', 1.0)

def hablar(texto):
    print(f"[ADNIA] {texto}")
    voz.say(texto)
    voz.runAndWait()

def analizar_pantalla():
    while True:
        # Captura la pantalla completa
        captura = ImageGrab.grab()
        # Extrae texto en español
        texto = pytesseract.image_to_string(captura, lang='spa')

        texto_lower = texto.lower()

        # Detecciones contextuales con voz
        if "modelo 303" in texto_lower:
            hablar("Veo el modelo 303 en pantalla. ¿Quieres que revise el IVA?")
        elif "irpf" in texto_lower:
            hablar("Estás en una pantalla de IRPF. Revisa las deducciones.")
        elif "aeat" in texto_lower or "agencia tributaria" in texto_lower:
            hablar("Estás en la web de Hacienda. Puedo ayudarte si lo necesitas.")
        elif "firma digital" in texto_lower:
            hablar("Estás a punto de firmar. ¿Quieres comprobar la validez jurídica antes?")
        elif "notificación" in texto_lower and "sede electrónica" in texto_lower:
            hablar("Has accedido a notificaciones oficiales. ¿Te ayudo a interpretarlas?")

        time.sleep(3)  # Espera 3 segundos antes de volver a capturar

def iniciar_copiloto_visual():
    print("🧠 ADNIA Copiloto Visual activo...")
    analizar_pantalla()
