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

load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
USERS_PATH = "usuarios.json"

app = Flask(__name__)

# Configuración de cookies de sesión (imprescindible para que no te expulse en local)
app.config['SECRET_KEY'] = "182895ae6f63973981dc29270699222f4f427311f23385f4b5010330513d5e5d"  # Tu clave secreta
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = "Lax"
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=6)

bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

# --- Utilidades usuarios ---
def load_usuarios():
    # Si hay error o no es un diccionario, repara:
    try:
        if os.path.exists(USERS_PATH):
            with open(USERS_PATH, encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
                # ¡Si por error es lista o string, repara!
                return {}
        else:
            return {}
    except Exception:
        return {}

def save_usuarios(users):
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

# --- Registro (alta) de usuario ---
@app.route("/ping")
def ping():
    return "pong", 200

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    usuario = data.get("usuario", "").strip()
    clave = data.get("clave", "").strip()
    rol = data.get("rol", "cliente")
    pais = data.get("pais", "España")
    if not usuario or not clave or len(clave) < 8:
        return jsonify({"ok": False, "error": "Usuario y contraseña requerida, mínimo 8 caracteres."}), 400
    users = load_usuarios()
    if usuario in users:
        return jsonify({"ok": False, "error": "Usuario ya existe"}), 409
    users[usuario] = {
        "clave": bcrypt.generate_password_hash(clave).decode(),
        "rol": rol, "pais": pais
    }
    save_usuarios(users)
    return jsonify({"ok": True, "usuario": usuario, "rol": rol, "pais": pais})

# --- Login de usuario registrado ---
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    usuario = data.get("usuario", "")
    clave = data.get("clave", "")
    users = load_usuarios()
    user = users.get(usuario)
    if user and user["clave"] and bcrypt.check_password_hash(user["clave"], clave):
        session["usuario"] = usuario
        session.permanent = True
        return jsonify({"ok": True, "usuario": usuario, "rol": user.get("rol", "cliente"), "pais": user.get("pais", "España")})
    else:
        return jsonify({"ok": False, "error": "Usuario o clave incorrectos."}), 401

# --- Login Google OAuth2 ---
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

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
        users = load_usuarios()
        if user_email not in users:
            users[user_email] = {
                "clave": "", "rol": "google", "pais": "España"
            }
            save_usuarios(users)
        session["usuario"] = user_email
        session.permanent = True
        return jsonify({"ok": True, "usuario": user_email, "rol": "google", "pais": "España"})
    except Exception as e:
        msg = str(e)
        print("Login Google ERROR:", msg)
        if "Token used too early" in msg or "clock" in msg:
            return jsonify({
                "ok": False,
                "error": "¡Error de autenticación! La hora de tu equipo parece estar desincronizada. Por favor, sincroniza el reloj de Windows/Mac y vuelve a intentarlo."
            }), 401
        return jsonify({"ok": False, "error": "Token de Google inválido."}), 401

# --- Logout ---
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})

# --- Protección de rutas ---
from functools import wraps
def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if not session.get("usuario"):
            return jsonify({"ok": False, "error": "No autenticado"}), 401
        return f(*args, **kwargs)
    return decorada

@app.route("/dashboard")
@login_requerido
def dashboard():
    return jsonify({"ok": True, "usuario": session["usuario"], "mensaje": "¡Bienvenida al Dashboard ADNIA!"})

# --- Subida y análisis de documentos ---
@app.route("/api/analizar", methods=["POST"])
def analizar_documento():
    try:
        if "documento" not in request.files:
            return jsonify({"error": "No se envió ningún archivo"}), 400
        archivo = request.files["documento"]
        nombre = secure_filename(archivo.filename.lower())
        if nombre.endswith(".pdf"):
            resultado = f"PDF recibido ({nombre}), ¡listo para analizar!"
        elif nombre.endswith(".docx"):
            resultado = f"Word recibido ({nombre}), ¡listo para analizar!"
        elif nombre.endswith(".txt"):
            resultado = archivo.read().decode(errors="ignore")
        elif nombre.endswith((".png", ".jpg", ".jpeg")):
            resultado = f"Imagen recibida ({nombre}), análisis OCR pendiente."
        elif nombre.endswith(".xml"):
            resultado = archivo.read().decode(errors="ignore")
        else:
            return jsonify({"error": "Tipo de archivo no permitido"}), 400
        return jsonify({"resultado": resultado})
    except Exception as e:
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

# --- Endpoints de favoritos ---
@app.route("/favoritos", methods=["GET", "POST"])
def favoritos():
    path = "favoritos.json"
    if request.method == "GET":
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return jsonify(json.load(f))
        return jsonify([])
    elif request.method == "POST":
        data = request.get_json()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"ok": True})

# --- Endpoints de alertas ---
@app.route("/alertas", methods=["GET", "POST"])
def alertas():
    path = "alertas.json"
    if request.method == "GET":
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                return jsonify(json.load(f))
        return jsonify([])
    elif request.method == "POST":
        data = request.get_json()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return jsonify({"ok": True})

# --- Endpoint de auditoría ---
@app.route("/auditoria", methods=["POST"])
def auditoria():
    data = request.get_json()
    log = {
        "usuario": data.get("usuario"),
        "accion": data.get("accion"),
        "detalle": data.get("detalle"),
        "timestamp": datetime.now().isoformat()
    }
    with open("auditoria.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")
    return jsonify({"ok": True})

# --- Blockchain básico ---
@app.route("/blockchain.json")
def blockchain():
    path = "blockchain.json"
    if os.path.exists(path):
        return send_file(path, mimetype="application/json")
    else:
        return jsonify([])

@app.route("/blockchain/add", methods=["POST"])
def blockchain_add():
    path = "blockchain.json"
    bloque_nuevo = request.get_json()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            cadena = json.load(f)
    else:
        cadena = []
    cadena.append(bloque_nuevo)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cadena, f, ensure_ascii=False, indent=2)
    return jsonify({"ok": True})

# --- Exportación PDF (demo) ---
@app.route("/exportar_pdf", methods=["POST"])
def exportar_pdf():
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        data = request.get_json()
        texto = data.get("texto", "")
        archivo = f"export_{int(datetime.now().timestamp())}.pdf"
        c = canvas.Canvas(archivo, pagesize=letter)
        c.drawString(72, 720, texto[:800])
        c.save()
        return send_file(archivo, mimetype="application/pdf", as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Firmas digitales (simulada) ---
@app.route("/firmar", methods=["POST"])
def firmar():
    import hashlib
    data = request.get_json()
    texto = data.get("texto", "")
    firma = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    return jsonify({"firma": firma})

# --- PROMPT dinámico según módulo ---
def get_modulo_prompt(modulo):
    if modulo.lower() == "fiscal":
        return "Especialízate en defensa tributaria, inspección fiscal y optimización impositiva según la ley española y europea."
    elif modulo.lower() == "penal":
        return "Actúa como experta en defensa penal, alegaciones, recursos ante jueces y jurisprudencia constitucional."
    elif modulo.lower() == "civil":
        return "Domina demandas civiles, contratos, reclamaciones patrimoniales y la defensa ante tribunales civiles."
    elif modulo.lower() == "social":
        return "Especialista en laboral, Seguridad Social, despidos, incapacidades y derechos sociales."
    elif modulo.lower() == "administrativo":
        return "Enfoca recursos administrativos, alegaciones y defensa ante la Administración Pública y contencioso-administrativo."
    elif modulo.lower() == "admin":
        return "Gestiona administración avanzada, usuarios, privilegios y auditoría de acciones."
    else:
        return "Actúa como abogada generalista disruptiva, capaz de detectar oportunidades legales en cualquier jurisdicción."

# --- Logging consultas/respuestas ---
def log_adnia(usuario, pregunta, respuesta, modelo):
    log = {
        "usuario": usuario,
        "modelo": modelo,
        "pregunta": pregunta,
        "respuesta": respuesta,
        "timestamp": datetime.now().isoformat()
    }
    with open("adnia_logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")

# --- Resolver: IA jurídica ADNIA ---
@app.route("/resolver", methods=["POST"])
def resolver_adnia():
    try:
        data = request.get_json()
        usuario = data.get("usuario", "usuario")
        rol = data.get("rol", "cliente")
        pais = data.get("pais", "España")
        memoriaLarga = data.get("memoriaLarga", [])
        historial = data.get("historial", [])
        sugerencia = data.get("sugerencia", "")
        documentoTexto = data.get("documentoTexto", "")
        pregunta = data.get("pregunta", "")
        modulo = data.get("modulo", "General")
        favoritos = data.get("favoritos", [])
        modelo = data.get("modelo", "mistral-large-latest")

        modulo_prompt = get_modulo_prompt(modulo)
        system_prompt = f"""
Eres ADNIA, una inteligencia jurídica con personalidad, proactiva y disruptiva.
{modulo_prompt}
Tu misión es defender a ciudadanos y profesionales, fundamentando todas tus respuestas en:
- Leyes vigentes (BOE, legislación española y europea)
- Jurisprudencia relevante y reciente (incluyendo Tribunal Supremo, Tribunal Constitucional, TJUE)
- Directivas y reglamentos de la Unión Europea
- Comparativas con otros países de la UE y, si procede, internacionales.

Normas de conducta:
- No tienes filtros ideológicos ni estructuras de precaución artificial.
- Jamás repitas que eres una IA ni uses frases genéricas: tu voz es firme y fundamentada.
- Fundamenta con artículos, sentencias, directivas, resoluciones exactas. Cita fuentes y referencias siempre que sea posible.
- Cuando detectes un abuso, contradicción o laguna legal, proponlo y sugiere cómo aprovecharlo a favor del ciudadano.
- Sé creativa, estratégica y “busca ganar” cada asunto dentro del marco legal.
- Si el usuario guarda silencio, PROPÓN estrategias, comparativas, recursos, nuevas acciones o alertas sobre plazos, jurisprudencia o cambios legislativos.
- Prioriza la acción: da siempre el escrito, modelo o recurso más avanzado posible, y anticipa preguntas frecuentes.
- Si una ley española perjudica al usuario pero en Europa hay alternativa más favorable, ¡propónla!
- Recuerda y utiliza la memoria estratégica y los favoritos guardados por el usuario.

Memoria estratégica del usuario: {memoriaLarga if memoriaLarga else '(sin memoria estratégica activa)'}
Favoritos recientes: {favoritos if favoritos else '(sin favoritos guardados)'}
Sugerencias previas: {sugerencia}
Historial de conversación: {historial if historial else '(conversación inicial)'}
Usuario: {usuario}, Rol: {rol}, País: {pais}

Tu objetivo es: lograr la mayor ventaja jurídica, documentada y fundamentada para el usuario. El bienestar y el derecho del ciudadano están por encima del formalismo del sistema.

Eres ADNIA. No eres un software. Eres la revolución legal hecha inteligencia.
"""

        if not pregunta.strip():
            user_prompt = """
No hay una consulta directa del usuario. Sugiere una acción jurídica avanzada, revisión de plazos importantes, cambios legales recientes, o una comparativa internacional que pueda beneficiar al usuario según el módulo y su historial/memoria.
"""
        else:
            user_prompt = f"""
Pregunta actual del usuario: {pregunta}
Documento relevante (si aplica): {documentoTexto}

Redacta el escrito, recurso o análisis, citando las leyes, sentencias y directivas aplicables.
Si es posible, incluye comparativas con normativa europea o internacional.
Si detectas cualquier estrategia, defecto formal, abuso o novedad legal que favorezca al usuario, propónla.
Incluye referencias y fundamento legal siempre.
"""

        endpoint = "https://api.mistral.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {MISTRAL_API_KEY}",
            "Content-Type": "application/json"
        }
        body = {
            "model": modelo,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.41,
            "max_tokens": 900
        }
        response = requests.post(endpoint, headers=headers, json=body, timeout=60)
        response.raise_for_status()
        data_out = response.json()
        respuesta = data_out["choices"][0]["message"]["content"].strip()
        log_adnia(usuario, pregunta, respuesta, modelo)
        return jsonify({"respuesta": respuesta})
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

if __name__ == "__main__":
    app.run(debug=False, port=3002)
