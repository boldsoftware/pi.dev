
terraform {
  required_version = ">=0.15.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
  }
}

provider "google" {
  project = var.project_id
}

provider "google-beta" {
  project = var.project_id
}

# Enable Certificate Manager API
resource "google_project_service" "certificate_manager" {
  project = var.project_id
  service = "certificatemanager.googleapis.com"
  disable_on_destroy = false
}
