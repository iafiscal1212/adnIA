#!/bin/bash

# Script de despliegue de ADNIA en Google Cloud Platform
# Autor: Manus AI
# Fecha: $(date)

set -e  # Salir si cualquier comando falla

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Verificar si gcloud está instalado
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud SDK no está instalado. Por favor, instálalo desde: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
    print_message "Google Cloud SDK encontrado"
}

# Verificar si Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker no está instalado. Por favor, instálalo desde: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_message "Docker encontrado"
}

# Configurar variables
setup_variables() {
    print_step "Configurando variables de entorno..."
    
    # Solicitar PROJECT_ID si no está configurado
    if [ -z "$PROJECT_ID" ]; then
        read -p "Ingresa tu Google Cloud Project ID: " PROJECT_ID
        export PROJECT_ID
    fi
    
    # Solicitar región si no está configurada
    if [ -z "$REGION" ]; then
        REGION="us-central1"
        print_message "Usando región por defecto: $REGION"
    fi
    
    # Solicitar nombre del servicio si no está configurado
    if [ -z "$SERVICE_NAME" ]; then
        SERVICE_NAME="adnia"
        print_message "Usando nombre de servicio por defecto: $SERVICE_NAME"
    fi
    
    print_message "PROJECT_ID: $PROJECT_ID"
    print_message "REGION: $REGION"
    print_message "SERVICE_NAME: $SERVICE_NAME"
}

# Autenticar con Google Cloud
authenticate() {
    print_step "Verificando autenticación con Google Cloud..."
    
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        print_warning "No hay cuentas autenticadas. Iniciando proceso de autenticación..."
        gcloud auth login
    else
        print_message "Ya estás autenticado con Google Cloud"
    fi
    
    # Configurar proyecto
    gcloud config set project $PROJECT_ID
    print_message "Proyecto configurado: $PROJECT_ID"
}

# Habilitar APIs necesarias
enable_apis() {
    print_step "Habilitando APIs necesarias..."
    
    apis=(
        "cloudbuild.googleapis.com"
        "run.googleapis.com"
        "containerregistry.googleapis.com"
        "artifactregistry.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        print_message "Habilitando $api..."
        gcloud services enable $api
    done
    
    print_message "APIs habilitadas correctamente"
}

# Construir imagen Docker
build_image() {
    print_step "Construyendo imagen Docker..."
    
    IMAGE_NAME="gcr.io/$PROJECT_ID/$SERVICE_NAME"
    BUILD_TAG=$(date +%Y%m%d-%H%M%S)
    FULL_IMAGE_NAME="$IMAGE_NAME:$BUILD_TAG"
    
    print_message "Construyendo imagen: $FULL_IMAGE_NAME"
    
    docker build -t $FULL_IMAGE_NAME .
    
    if [ $? -eq 0 ]; then
        print_message "Imagen construida exitosamente"
        export FULL_IMAGE_NAME
    else
        print_error "Error al construir la imagen Docker"
        exit 1
    fi
}

# Subir imagen al Container Registry
push_image() {
    print_step "Subiendo imagen al Container Registry..."
    
    # Configurar Docker para usar gcloud como helper de credenciales
    gcloud auth configure-docker
    
    print_message "Subiendo imagen: $FULL_IMAGE_NAME"
    docker push $FULL_IMAGE_NAME
    
    if [ $? -eq 0 ]; then
        print_message "Imagen subida exitosamente"
    else
        print_error "Error al subir la imagen"
        exit 1
    fi
}

# Desplegar en Cloud Run
deploy_cloudrun() {
    print_step "Desplegando en Cloud Run..."
    
    print_message "Desplegando servicio: $SERVICE_NAME"
    print_message "Imagen: $FULL_IMAGE_NAME"
    print_message "Región: $REGION"
    
    gcloud run deploy $SERVICE_NAME \
        --image $FULL_IMAGE_NAME \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 2Gi \
        --cpu 2 \
        --max-instances 10 \
        --min-instances 1 \
        --timeout 300 \
        --set-env-vars "FLASK_ENV=production"
    
    if [ $? -eq 0 ]; then
        print_message "Despliegue completado exitosamente"
        
        # Obtener URL del servicio
        SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format 'value(status.url)')
        print_message "URL del servicio: $SERVICE_URL"
        
        # Guardar información del despliegue
        echo "ADNIA desplegado exitosamente en Google Cloud Platform" > deployment_info.txt
        echo "Fecha: $(date)" >> deployment_info.txt
        echo "Proyecto: $PROJECT_ID" >> deployment_info.txt
        echo "Servicio: $SERVICE_NAME" >> deployment_info.txt
        echo "Región: $REGION" >> deployment_info.txt
        echo "Imagen: $FULL_IMAGE_NAME" >> deployment_info.txt
        echo "URL: $SERVICE_URL" >> deployment_info.txt
        
        print_message "Información del despliegue guardada en deployment_info.txt"
    else
        print_error "Error en el despliegue"
        exit 1
    fi
}

# Configurar variables de entorno (opcional)
configure_env_vars() {
    print_step "¿Deseas configurar variables de entorno adicionales? (y/n)"
    read -p "Respuesta: " configure_env
    
    if [ "$configure_env" = "y" ] || [ "$configure_env" = "Y" ]; then
        print_message "Configurando variables de entorno..."
        
        # Ejemplo de configuración de variables de entorno
        print_warning "Recuerda configurar las siguientes variables si las necesitas:"
        echo "- MISTRAL_API_KEY: Tu clave API de Mistral"
        echo "- GOOGLE_CLIENT_ID: Tu Client ID de Google OAuth"
        echo "- Otras variables específicas de tu aplicación"
        
        print_message "Puedes configurar estas variables usando:"
        echo "gcloud run services update $SERVICE_NAME --region $REGION --set-env-vars KEY=VALUE"
    fi
}

# Función principal
main() {
    print_message "=== DESPLIEGUE DE ADNIA EN GOOGLE CLOUD PLATFORM ==="
    print_message "Este script desplegará ADNIA en Google Cloud Run"
    echo
    
    # Verificaciones previas
    check_gcloud
    check_docker
    
    # Configuración
    setup_variables
    authenticate
    enable_apis
    
    # Construcción y despliegue
    build_image
    push_image
    deploy_cloudrun
    
    # Configuración adicional
    configure_env_vars
    
    print_message "=== DESPLIEGUE COMPLETADO ==="
    print_message "ADNIA está ahora disponible en Google Cloud Platform"
    print_message "Revisa deployment_info.txt para más detalles"
}

# Ejecutar función principal
main "$@"

