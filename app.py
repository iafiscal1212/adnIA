import os
import re
import json
import traceback
from flask import Flask, request, jsonify, session, send_file
from flask_session import Session 
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from dotenv import load_dotenv
from datetime import timedelta, datetime
from werkzeug.utils import secure_filename
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from flask_sqlalchemy import SQLAlchemy
from google.cloud import storage
from functools import wraps

load_dotenv()

# Variables de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/adnia.db")
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key_for_prod")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
ADMIN_SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "default-admin-secret-for-dev-only")

# Instancia de la aplicación Flask
app = Flask(__name__)

# Configuración de base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', 'False').lower() in ('true', '1', 't')
db = SQLAlchemy(app)

# Configuración de sesiones
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=6)

# Clientes de servicios
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)
storage_client = storage.Client()
bucket = storage_client.bucket(GCS_BUCKET_NAME)

# --- Modelos de base de datos ---
class User(db.Model):
    __tablename__ = 'adnia_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    rol = db.Column(db.String(50), nullable=False, default='cliente')
    pais = db.Column(db.String(50), nullable=True, default='España')
    google_id = db.Column(db.String(255), unique=True, nullable=True)

    def __repr__(self):
        return f'<User {self.email}>'

class Document(db.Model):
    __tablename__ = 'adnia_documents'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('adnia_users.id'), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    gcs_path = db.Column(db.String(512), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<Document {self.file_name}>'

# --- Utilidades generales ---
def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get("usuario"):
            return jsonify({"ok": False, "error": "No autenticado"}), 401
        return f(*args, **kwargs)
    return decorada

def create_db_tables():
    with app.app_context():
        print("Creando tablas de base de datos si no existen...")
        db.create_all()
        print("Tablas verificadas/creadas.")

# --- Endpoints ---
@app.route("/")
def home():
    return send_file("static/index.html")

@app.route("/ping")
def ping():
    try:
        db.session.execute(db.text('SELECT 1'))
        return "pong (database connected)", 200
    except Exception:
        return "pong (database not connected)", 500

@app.route("/login-google", methods=["POST"])
def login_google():
    data = request.get_json()
    token_id = data.get("token_id")
    try:
        idinfo = id_token.verify_oauth2_token(
            token_id,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )
        user_email = idinfo["email"]
        user = User.query.filter_by(email=user_email).first()
        if not user:
            user = User(email=user_email, rol="google")
            db.session.add(user)
            db.session.commit()
        session["usuario_id"] = user.id
        session.permanent = True
        return jsonify({"ok": True, "usuario": user.email, "rol": user.rol})
    except Exception as e:
        msg = str(e)
        print("Login Google ERROR:", msg)
        return jsonify({"ok": False, "error": "Token de Google inválido o caducado."}), 401

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/dashboard")
@login_requerido
def dashboard():
    user_id = session.get("usuario_id")
    user = User.query.get(user_id)
    if user:
        return jsonify({"ok": True, "usuario": user.email, "mensaje": "¡Bienvenida al Dashboard ADNIA!"})
    return jsonify({"ok": False, "error": "Usuario no encontrado"}), 404

# --- Subida y gestión de documentos ---
@app.route("/upload-document", methods=["POST"])
@login_requerido
def upload_document():
    try:
        if "documento" not in request.files:
            return jsonify({"ok": False, "error": "No se envió ningún archivo"}), 400
        
        file = request.files["documento"]
        filename = secure_filename(file.filename)
        user_id = session.get("usuario_id")
        
        # Subir a Google Cloud Storage
        blob_path = f"users/{user_id}/{filename}"
        blob = bucket.blob(blob_path)
        blob.upload_from_file(file)

        # Guardar metadatos en la base de datos
        new_document = Document(user_id=user_id, file_name=filename, gcs_path=blob_path)
        db.session.add(new_document)
        db.session.commit()

        return jsonify({"ok": True, "mensaje": "Documento subido y guardado."}), 200
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/list-documents", methods=["GET"])
@login_requerido
def list_documents():
    user_id = session.get("usuario_id")
    documents = Document.query.filter_by(user_id=user_id).all()
    
    document_list = []
    for doc in documents:
        document_list.append({
            "id": doc.id,
            "file_name": doc.file_name,
            "created_at": doc.created_at.isoformat()
        })
    
    return jsonify({"ok": True, "documentos": document_list}), 200

@app.route("/get-document-url/<int:doc_id>", methods=["GET"])
@login_requerido
def get_document_url(doc_id):
    try:
        user_id = session.get("usuario_id")
        doc = Document.query.filter_by(id=doc_id, user_id=user_id).first()
        if not doc:
            return jsonify({"ok": False, "error": "Documento no encontrado o no autorizado."}), 404

        blob = bucket.blob(doc.gcs_path)
        signed_url = blob.generate_signed_url(expiration=timedelta(minutes=15))

        return jsonify({"ok": True, "url": signed_url}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# Endpoint de administración para crear tablas
@app.route("/admin/create-tables", methods=['POST'])
def admin_create_tables():
    provided_key = request.headers.get('X-Admin-Secret-Key')
    if provided_key != ADMIN_SECRET_KEY:
        return jsonify({"ok": False, "error": "Acceso no autorizado"}), 401
    
    try:
        create_db_tables()
        return jsonify({"ok": True, "message": "Tablas verificadas/creadas."}), 200
    except Exception as e:
        print(f"Error en /admin/create-tables: {traceback.format_exc()}")
        return jsonify({"ok": False, "error": f"Error al crear tablas: {str(e)}"}), 500


# Endpoint principal para iniciar la aplicación si se ejecuta directamente
if __name__ == "__main__":
    with app.app_context():
        create_db_tables()
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=False, host="0.0.0.0", port=port)
