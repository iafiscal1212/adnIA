import os
import json
import time
from langchain_openai import ChatOpenAI
from langchain_mistralai.chat_models import ChatMistralAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults

# ¡NUEVO! Imports para Google Cloud Vision y Storage
from google.cloud import vision
from google.cloud import storage
import pypdf

from humanshield_module_adnia import humanize_with_humbot

# --- Inicialización de Clientes de Google Cloud ---
storage_client = storage.Client()
vision_client = vision.ImageAnnotatorClient()


# --- ¡NUEVA HERRAMIENTA CON GOOGLE VISION! ---
@tool
def analyze_document_with_google(gcs_path: str) -> str:
    """
    Analiza el contenido de un archivo (PDF o imagen) almacenado en Google Cloud Storage (GCS)
    utilizando la API de Google Cloud Vision y devuelve el texto extraído.
    El input debe ser la ruta GCS del archivo, por ejemplo: 'bucket-name/path/to/file.pdf'.
    """
    try:
        bucket_name, blob_name = gcs_path.split('/', 1)
        
        gcs_source_uri = f"gs://{gcs_path}"
        gcs_destination_uri = f"gs://{bucket_name}/ocr_results/{blob_name}_"

        # Determinar el tipo de archivo
        blob = storage_client.bucket(bucket_name).get_blob(blob_name)
        file_content = blob.download_as_bytes()
        
        mime_type = 'application/pdf' if blob.content_type == 'application/pdf' or blob_name.lower().endswith('.pdf') else 'image/png'

        if mime_type == 'application/pdf':
            # Proceso asíncrono para PDFs
            feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
            gcs_source = vision.GcsSource(uri=gcs_source_uri)
            input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)
            
            gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
            output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=20)
            
            async_request = vision.AsyncAnnotateFileRequest(
                features=[feature], input_config=input_config, output_config=output_config
            )

            operation = vision_client.async_batch_annotate_files(requests=[async_request])
            operation.result(timeout=420) # Esperar a que termine el proceso

            # Leer el resultado del OCR desde GCS
            bucket = storage_client.get_bucket(bucket_name)
            blob_list = [blob for blob in bucket.list_blobs(prefix=f"ocr_results/{blob_name}_")]
            
            output_text = ""
            for blob_item in blob_list:
                json_string = blob_item.download_as_string()
                response = json.loads(json_string)
                for page_response in response['responses']:
                    output_text += page_response['fullTextAnnotation']['text']
                blob_item.delete() # Limpiar el archivo de resultados

            return output_text[:8000]

        else: # Para imágenes (proceso síncrono)
            image = vision.Image(content=file_content)
            response = vision_client.text_detection(image=image)
            if response.error.message:
                raise Exception(f"Error en la API de Vision: {response.error.message}")
            return response.full_text_annotation.text[:8000]

    except Exception as e:
        return f"Error al analizar el documento con Google Vision: {e}"

# ... (El resto de tu código de adnia_agents.py con las herramientas de búsqueda, etc., se mantiene igual)
# Asegúrate de añadir la nueva herramienta a tu lista `tools`.
tools = [analyze_document_with_google, buscar_en_boe, ...]
