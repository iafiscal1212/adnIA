## Configuración para Despliegue en Google Cloud Run

Para desplegar esta aplicación en Google Cloud Run, es crucial configurar las siguientes variables de entorno en el servicio de Cloud Run.

### Base de Datos

*   `SQLALCHEMY_DATABASE_URI`: La cadena de conexión a la base de datos.
    *   **Para desarrollo/pruebas rápidas (predeterminado):** No es necesario establecer esta variable. La aplicación usará `sqlite:////tmp/adnia.db`, una base de datos temporal en el sistema de archivos de Cloud Run. **Nota:** Esta base de datos se eliminará cada vez que la instancia se reinicie.
    *   **Para producción:** Debes usar una base de datos persistente como Google Cloud SQL. Ejemplo para PostgreSQL:
        `postgresql+psycopg2://<USUARIO>:<CONTRASEÑA>@<IP_O_RUTA_SOCKET>/<NOMBRE_DB>`

*   `SQLALCHEMY_TRACK_MODIFICATIONS`: Controla el seguimiento de modificaciones de SQLAlchemy.
    *   **Valor recomendado:** `False` (esto también es el predeterminado).

### Autenticación y Otros Servicios

*   `SECRET_KEY`: Una clave secreta y larga para firmar las sesiones de Flask.
*   `GOOGLE_CLIENT_ID`: El ID de cliente de OAuth 2.0 de Google para el inicio de sesión de Google.
*   `GOOGLE_CLIENT_SECRET`: El secreto de cliente de OAuth 2.0 de Google.
*   `GCS_BUCKET_NAME`: El nombre del bucket de Google Cloud Storage donde se almacenan los documentos.
*   `ADMIN_SECRET_KEY`: Una clave secreta para acceder a los endpoints de administración.
*   `OPENAI_API_KEY`: Tu clave de API de OpenAI para que los agentes de LangChain puedan acceder a los modelos de lenguaje.

### Ejemplo de Configuración en `gcloud`

```bash
gcloud run deploy adnia-backend \\
  --image gcr.io/adnia-459219/adnia-backend \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --set-env-vars="SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://user:pass@host/dbname" \\
  --set-env-vars="SECRET_KEY=tu-clave-secreta-muy-larga" \\
  --set-env-vars="GOOGLE_CLIENT_ID=tu-id-de-cliente.apps.googleusercontent.com" \\
  --set-env-vars="GOOGLE_CLIENT_SECRET=tu-secreto-de-cliente" \\
  --set-env-vars="GCS_BUCKET_NAME=tu-bucket-de-gcs" \\
  --set-env-vars="ADMIN_SECRET_KEY=tu-clave-de-admin"
```
