# prototyper_backend.py
# Motor de prototipado legal y empresarial para ADNIA

from fastapi import FastAPI, Request, UploadFile, File
from pydantic import BaseModel
import os
import mimetypes
import fitz  # PyMuPDF para PDFs
from docx import Document
import pytesseract
from PIL import Image
import io

app = FastAPI()

class Instruccion(BaseModel):
    idea: str

@app.post("/prototyper")
def generar_modulo(req: Instruccion):
    idea = req.idea.lower()
    resultado = ""

    if "contrato" in idea:
        resultado = "Plantilla de contrato generada con cláusulas estándar para compraventa, confidencialidad o prestación de servicios."
    elif "formulario fiscal" in idea:
        resultado = "Formulario web con campos para IRPF, IVA, CIF/NIF y cálculo automático de liquidaciones."
    elif "certificado digital" in idea:
        resultado = "Panel de gestión de certificados digitales: subida, validación, vencimientos y alertas."
    elif "boe" in idea:
        resultado = "Scraper conectado al BOE para detectar normas fiscales o cambios jurídicos relevantes."
    elif "nómina" in idea or "laboral" in idea:
        resultado = "Simulador de nómina para empresa con IRPF, Seguridad Social y extras opcionales."
    elif "análisis financiero" in idea:
        resultado = "Módulo de lectura de balances con cálculo de ratios y visualización gráfica."
    else:
        resultado = "Módulo genérico creado. Se recomienda revisión manual para ideas no reconocidas."

    return {"prototipo": resultado}

@app.post("/analizar-archivo")
def analizar_archivo(file: UploadFile = File(...)):
    nombre = file.filename
    extension = os.path.splitext(nombre)[1].lower()
    contenido = ""

    if extension == ".pdf":
        pdf = fitz.open(stream=file.file.read(), filetype="pdf")
        for page in pdf:
            contenido += page.get_text()
        pdf.close()
    elif extension == ".docx":
        doc = Document(file.file)
        contenido = "\n".join([p.text for p in doc.paragraphs])
    elif extension == ".html":
        contenido = file.file.read().decode("utf-8")
    elif extension == ".txt":
        contenido = file.file.read().decode("utf-8")
    elif extension == ".png":
        image = Image.open(io.BytesIO(file.file.read()))
        contenido = pytesseract.image_to_string(image)
    else:
        contenido = "Tipo de archivo no soportado todavía."

    return {"nombre": nombre, "contenido": contenido[:2000]}

# Para lanzar: uvicorn prototyper_backend:app --reload
