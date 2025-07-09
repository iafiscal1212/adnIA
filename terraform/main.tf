# Configuración de Terraform para ADNIA en Google Cloud Platform
# Autor: Manus AI

terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

# Variables
variable "project_id" {
  description = "Google Cloud Project ID"
  type        = string
}

variable "region" {
  description = "Google Cloud Region"
  type        = string
  default     = "us-central1"
}

variable "service_name" {
  description = "Nombre del servicio Cloud Run"
  type        = string
  default     = "adnia"
}

variable "image_url" {
  description = "URL de la imagen Docker"
  type        = string
}

variable "mistral_api_key" {
  description = "Clave API de Mistral"
  type        = string
  sensitive   = true
  default     = ""
}

variable "google_client_id" {
  description = "Google OAuth Client ID"
  type        = string
  default     = ""
}

# Proveedor de Google Cloud
provider "google" {
  project = var.project_id
  region  = var.region
}

# Habilitar APIs necesarias
resource "google_project_service" "cloud_run_api" {
  service = "run.googleapis.com"
}

resource "google_project_service" "cloud_build_api" {
  service = "cloudbuild.googleapis.com"
}

resource "google_project_service" "container_registry_api" {
  service = "containerregistry.googleapis.com"
}

resource "google_project_service" "artifact_registry_api" {
  service = "artifactregistry.googleapis.com"
}

# Servicio Cloud Run
resource "google_cloud_run_service" "adnia" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        image = var.image_url
        
        ports {
          container_port = 8080
        }
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "2Gi"
          }
        }
        
        env {
          name  = "FLASK_ENV"
          value = "production"
        }
        
        env {
          name  = "PYTHONPATH"
          value = "/app"
        }
        
        dynamic "env" {
          for_each = var.mistral_api_key != "" ? [1] : []
          content {
            name  = "MISTRAL_API_KEY"
            value = var.mistral_api_key
          }
        }
        
        dynamic "env" {
          for_each = var.google_client_id != "" ? [1] : []
          content {
            name  = "GOOGLE_CLIENT_ID"
            value = var.google_client_id
          }
        }
      }
      
      container_concurrency = 80
      timeout_seconds      = 300
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "10"
        "run.googleapis.com/cpu-throttling" = "false"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_project_service.cloud_run_api]
}

# Política IAM para permitir acceso público
resource "google_cloud_run_service_iam_member" "public_access" {
  service  = google_cloud_run_service.adnia.name
  location = google_cloud_run_service.adnia.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Outputs
output "service_url" {
  description = "URL del servicio Cloud Run"
  value       = google_cloud_run_service.adnia.status[0].url
}

output "service_name" {
  description = "Nombre del servicio"
  value       = google_cloud_run_service.adnia.name
}

output "service_location" {
  description = "Ubicación del servicio"
  value       = google_cloud_run_service.adnia.location
}

