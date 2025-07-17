# Archivo: ingest.py
import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

load_dotenv()

if os.getenv("GOOGLE_API_KEY") is None:
    raise ValueError("La clave de API de Google no se encontró en las variables de entorno.")

def create_vector_db():
    """Lee documentos, los divide, crea embeddings y los guarda en una base de datos FAISS."""
    loader = DirectoryLoader('legal_docs/', glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
    documents = loader.load()
    print(f"Se han cargado {len(documents)} documentos.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    print(f"Se han creado {len(chunks)} trozos de texto (chunks).")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    
    db = FAISS.from_documents(chunks, embeddings)
    db.save_local("faiss_index")
    print("¡Base de datos vectorial creada y guardada como 'faiss_index'!")

if __name__ == "__main__":
    create_vector_db()
