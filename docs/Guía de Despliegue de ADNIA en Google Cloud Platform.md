# Guía de Despliegue de ADNIA en Google Cloud Platform

**Autor:** Manus AI  
**Fecha:** $(date)  
**Versión:** 1.0

## Introducción

Esta guía proporciona instrucciones detalladas para desplegar ADNIA (Asistente Digital de Navegación e Inteligencia Artificial) en Google Cloud Platform (GCP). ADNIA es una aplicación de inteligencia artificial jurídica diseñada para defender al pueblo y pequeños empresarios, proporcionando asesoramiento legal especializado por jurisdicciones.

## Tabla de Contenidos

1. [Prerrequisitos](#prerrequisitos)
2. [Opciones de Despliegue](#opciones-de-despliegue)
3. [Método 1: Despliegue Automático con Script](#método-1-despliegue-automático-con-script)
4. [Método 2: Despliegue Manual](#método-2-despliegue-manual)
5. [Método 3: Despliegue con Terraform](#método-3-despliegue-con-terraform)
6. [Método 4: Despliegue en App Engine](#método-4-despliegue-en-app-engine)
7. [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
8. [Verificación del Despliegue](#verificación-del-despliegue)
9. [Monitoreo y Logs](#monitoreo-y-logs)
10. [Solución de Problemas](#solución-de-problemas)
11. [Mantenimiento y Actualizaciones](#mantenimiento-y-actualizaciones)
12. [Consideraciones de Seguridad](#consideraciones-de-seguridad)
13. [Estimación de Costos](#estimación-de-costos)

## Prerrequisitos

### Cuenta y Proyecto de Google Cloud

1. **Cuenta de Google Cloud**: Necesitas una cuenta activa de Google Cloud Platform
2. **Proyecto de GCP**: Crea un nuevo proyecto o utiliza uno existente
3. **Facturación habilitada**: Asegúrate de que la facturación esté habilitada en tu proyecto
4. **Permisos necesarios**: Tu cuenta debe tener los siguientes roles:
   - Editor del proyecto o roles específicos:
     - Cloud Run Admin
     - Storage Admin
     - Service Account User
     - Cloud Build Editor

### Herramientas Locales

1. **Google Cloud SDK (gcloud)**
   ```bash
   # Instalación en Ubuntu/Debian
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

2. **Docker**
   ```bash
   # Instalación en Ubuntu
   sudo apt-get update
   sudo apt-get install docker.io
   sudo usermod -aG docker $USER
   ```

3. **Git** (para clonar el repositorio)
   ```bash
   sudo apt-get install git
   ```

4. **Terraform** (opcional, para infraestructura como código)
   ```bash
   wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
   unzip terraform_1.6.0_linux_amd64.zip
   sudo mv terraform /usr/local/bin/
   ```

### Configuración Inicial

1. **Autenticación con Google Cloud**
   ```bash
   gcloud auth login
   gcloud config set project TU_PROJECT_ID
   ```

2. **Habilitar APIs necesarias**
   ```bash
   gcloud services enable cloudbuild.googleapis.com
   gcloud services enable run.googleapis.com
   gcloud services enable containerregistry.googleapis.com
   ```

## Opciones de Despliegue

ADNIA puede desplegarse en GCP utilizando diferentes servicios, cada uno con sus ventajas:

### Cloud Run (Recomendado)
- **Ventajas**: Serverless, escalado automático, pago por uso
- **Ideal para**: Aplicaciones con tráfico variable
- **Costo**: Muy económico para aplicaciones pequeñas a medianas

### App Engine
- **Ventajas**: Totalmente administrado, fácil de usar
- **Ideal para**: Aplicaciones web tradicionales
- **Costo**: Predecible, bueno para tráfico constante

### Compute Engine
- **Ventajas**: Control total, personalización completa
- **Ideal para**: Aplicaciones que requieren configuración específica
- **Costo**: Más alto, requiere administración

## Método 1: Despliegue Automático con Script

Este es el método más rápido y recomendado para la mayoría de usuarios.

### Paso 1: Preparar el Entorno

```bash
# Clonar o descargar el proyecto ADNIA
cd ADNIA_CORE_GCP

# Verificar que todos los archivos estén presentes
ls -la
```

### Paso 2: Configurar Variables

```bash
# Configurar variables de entorno
export PROJECT_ID="tu-proyecto-gcp"
export REGION="us-central1"
export SERVICE_NAME="adnia"
```

### Paso 3: Ejecutar Script de Despliegue

```bash
# Hacer el script ejecutable (si no lo está)
chmod +x deploy.sh

# Ejecutar el despliegue
./deploy.sh
```

El script realizará automáticamente:
- Verificación de prerrequisitos
- Autenticación con GCP
- Habilitación de APIs
- Construcción de la imagen Docker
- Subida al Container Registry
- Despliegue en Cloud Run
- Configuración de acceso público

### Paso 4: Verificar el Despliegue

Al finalizar, el script mostrará la URL de tu aplicación. Visita esa URL para verificar que ADNIA esté funcionando correctamente.

## Método 2: Despliegue Manual

Si prefieres tener control total sobre cada paso, puedes realizar el despliegue manualmente.

### Paso 1: Construir la Imagen Docker

```bash
# Navegar al directorio del proyecto
cd ADNIA_CORE_GCP

# Construir la imagen
docker build -t gcr.io/TU_PROJECT_ID/adnia:latest .
```

### Paso 2: Subir la Imagen

```bash
# Configurar Docker para GCP
gcloud auth configure-docker

# Subir la imagen
docker push gcr.io/TU_PROJECT_ID/adnia:latest
```

### Paso 3: Desplegar en Cloud Run

```bash
gcloud run deploy adnia \
    --image gcr.io/TU_PROJECT_ID/adnia:latest \
    --region us-central1 \
    --platform managed \
    --allow-unauthenticated \
    --port 8080 \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10 \
    --min-instances 1 \
    --timeout 300
```

### Paso 4: Configurar Variables de Entorno

```bash
gcloud run services update adnia \
    --region us-central1 \
    --set-env-vars "FLASK_ENV=production,MISTRAL_API_KEY=tu_clave_api"
```

## Método 3: Despliegue con Terraform

Para un enfoque de infraestructura como código, utiliza Terraform.

### Paso 1: Configurar Terraform

```bash
cd terraform

# Copiar archivo de variables
cp terraform.tfvars.example terraform.tfvars

# Editar variables
nano terraform.tfvars
```

### Paso 2: Inicializar Terraform

```bash
terraform init
```

### Paso 3: Planificar el Despliegue

```bash
terraform plan
```

### Paso 4: Aplicar la Configuración

```bash
terraform apply
```

### Paso 5: Obtener Outputs

```bash
terraform output service_url
```

## Método 4: Despliegue en App Engine

Para usar App Engine en lugar de Cloud Run:

### Paso 1: Preparar app.yaml

El archivo `app.yaml` ya está incluido en el proyecto.

### Paso 2: Desplegar

```bash
gcloud app deploy app.yaml
```

### Paso 3: Abrir la Aplicación

```bash
gcloud app browse
```

## Configuración de Variables de Entorno

ADNIA requiere ciertas variables de entorno para funcionar correctamente:

### Variables Requeridas

- `FLASK_ENV`: Debe ser "production" para el entorno de producción
- `MISTRAL_API_KEY`: Tu clave API de Mistral para la funcionalidad de IA

### Variables Opcionales

- `GOOGLE_CLIENT_ID`: Para autenticación con Google OAuth
- `PORT`: Puerto de la aplicación (automático en Cloud Run)

### Configurar en Cloud Run

```bash
gcloud run services update adnia \
    --region us-central1 \
    --set-env-vars "MISTRAL_API_KEY=tu_clave,GOOGLE_CLIENT_ID=tu_client_id"
```

### Configurar en App Engine

Edita el archivo `app.yaml`:

```yaml
env_variables:
  MISTRAL_API_KEY: "tu_clave_api"
  GOOGLE_CLIENT_ID: "tu_client_id"
```

## Verificación del Despliegue

### Pruebas Básicas

1. **Endpoint de salud**
   ```bash
   curl https://tu-servicio-url/ping
   ```

2. **Interfaz web**
   Visita la URL en tu navegador y verifica que la interfaz carga correctamente.

3. **Funcionalidad de IA**
   Prueba hacer una consulta legal para verificar que la integración con Mistral funciona.

### Pruebas de Carga

```bash
# Instalar herramientas de prueba
sudo apt-get install apache2-utils

# Prueba de carga básica
ab -n 100 -c 10 https://tu-servicio-url/ping
```

## Monitoreo y Logs

### Ver Logs en Cloud Run

```bash
gcloud run services logs read adnia --region us-central1
```

### Monitoreo en la Consola

1. Ve a la consola de Google Cloud
2. Navega a Cloud Run > tu servicio
3. Ve a la pestaña "Logs" para ver logs en tiempo real
4. Ve a la pestaña "Métricas" para ver estadísticas de uso

### Configurar Alertas

```bash
# Crear política de alerta para errores
gcloud alpha monitoring policies create --policy-from-file=alert-policy.yaml
```

## Solución de Problemas

### Problemas Comunes

1. **Error de autenticación**
   ```bash
   gcloud auth login
   gcloud config set project TU_PROJECT_ID
   ```

2. **Error de permisos**
   Verifica que tu cuenta tenga los roles necesarios en IAM.

3. **Error de construcción de imagen**
   Verifica que Docker esté funcionando:
   ```bash
   docker --version
   sudo systemctl start docker
   ```

4. **Error de memoria**
   Aumenta la memoria asignada:
   ```bash
   gcloud run services update adnia --memory 4Gi
   ```

5. **Timeout de requests**
   Aumenta el timeout:
   ```bash
   gcloud run services update adnia --timeout 600
   ```

### Logs de Depuración

```bash
# Ver logs detallados
gcloud run services logs read adnia --region us-central1 --limit 50

# Ver logs en tiempo real
gcloud run services logs tail adnia --region us-central1
```

## Mantenimiento y Actualizaciones

### Actualizar la Aplicación

1. **Hacer cambios en el código**
2. **Reconstruir la imagen**
   ```bash
   docker build -t gcr.io/TU_PROJECT_ID/adnia:v2 .
   docker push gcr.io/TU_PROJECT_ID/adnia:v2
   ```
3. **Desplegar nueva versión**
   ```bash
   gcloud run deploy adnia --image gcr.io/TU_PROJECT_ID/adnia:v2
   ```

### Rollback

```bash
# Ver revisiones
gcloud run revisions list --service adnia

# Hacer rollback
gcloud run services update-traffic adnia --to-revisions REVISION_NAME=100
```

### Backup de Datos

```bash
# Backup de archivos JSON
gsutil cp *.json gs://tu-bucket-backup/
```

## Consideraciones de Seguridad

### Autenticación y Autorización

1. **Configurar IAM apropiadamente**
2. **Usar Service Accounts específicos**
3. **Implementar autenticación en la aplicación**

### Secretos

1. **Usar Secret Manager para API keys**
   ```bash
   gcloud secrets create mistral-api-key --data-file=key.txt
   ```

2. **Configurar acceso a secretos**
   ```bash
   gcloud run services update adnia \
       --update-secrets MISTRAL_API_KEY=mistral-api-key:latest
   ```

### Red y Firewall

1. **Configurar VPC si es necesario**
2. **Implementar Cloud Armor para protección DDoS**
3. **Configurar SSL/TLS (automático en Cloud Run)**

## Estimación de Costos

### Cloud Run (Recomendado)

Para una aplicación con uso moderado:
- **CPU**: $0.000024 por vCPU-segundo
- **Memoria**: $0.0000025 por GiB-segundo
- **Requests**: $0.40 por millón de requests

**Estimación mensual**: $10-50 USD para uso típico

### App Engine

- **Instancia F1**: $0.05 por hora
- **Estimación mensual**: $36 USD (instancia siempre activa)

### Storage y Networking

- **Container Registry**: $0.026 por GB/mes
- **Egress**: $0.12 por GB (después de 1GB gratis)

### Optimización de Costos

1. **Configurar escalado automático apropiado**
2. **Usar instancias mínimas = 0 si es aceptable cold start**
3. **Monitorear uso regularmente**
4. **Implementar cache para reducir compute**

---

## Conclusión

Esta guía proporciona múltiples métodos para desplegar ADNIA en Google Cloud Platform, desde el más simple (script automático) hasta el más avanzado (Terraform). Elige el método que mejor se adapte a tus necesidades y nivel de experiencia.

Para soporte adicional o preguntas específicas, consulta la documentación oficial de Google Cloud Platform o contacta al equipo de desarrollo de ADNIA.

**¡ADNIA está listo para defender al pueblo en la nube!**

