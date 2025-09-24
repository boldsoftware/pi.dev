locals {
  common_labels = {
    environment = "production"
    project     = var.project_id
  }
}

data "google_compute_default_service_account" "default" {
  project = var.project_id
}

resource "google_project_iam_member" "compute_roles" {
  for_each = toset([
    "roles/logging.logWriter",
    "roles/cloudbuild.builds.editor",
    "roles/artifactregistry.writer",
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/serviceusage.serviceUsageConsumer",

    # Not sure why this is necessary; would like to remove it
    "roles/storage.admin"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${data.google_compute_default_service_account.default.email}"
}

resource "google_service_account" "scheduler_sa" {
  project      = var.project_id
  account_id   = var.service_account_id
  display_name = "Scheduler Invoker Service Account"
}

resource "google_service_account" "podcast_generator_service_sa" {
  project      = var.project_id
  account_id   = "podcast-generator-service-sa"
  display_name = "Podcast generator Service Account"
}

resource "google_service_account" "web_service_sa" {
  project      = var.project_id
  account_id   = "web-service-sa"
  display_name = "Web Service Account"
}

resource "google_service_account" "ci_cd_sa" {
  project      = var.project_id
  account_id   = "pi-dev-ci-cd"
  display_name = "pi.dev CI/CD Service Account"
}

# IAM Roles for Cloud Run Service Account
resource "google_project_iam_member" "ci_cd_roles" {
  for_each = toset([
    "roles/cloudbuild.builds.editor",
    "roles/artifactregistry.writer",
    "roles/run.admin",
    "roles/iam.serviceAccountUser",
    "roles/serviceusage.serviceUsageConsumer",

    # Not sure why this is necessary; would like to remove it
    "roles/storage.admin"
  ])

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.ci_cd_sa.email}"
}

resource "google_artifact_registry_repository" "pi_registry" {
  project       = var.project_id
  location      = var.region
  repository_id = "pi-registry"
  description   = "Artifact Registry for pi-dev images"
  format        = "DOCKER"

  labels = {
    environment = "production"
    project     = var.project_id
  }
}

data "google_secret_manager_secret" "github_app_private_key" {
  project   = var.project_id
  secret_id = var.github_secret_name
}

data "google_secret_manager_secret" "openai_api_key" {
  project   = var.project_id
  secret_id = var.open_ai_secret_name
}

data "google_secret_manager_secret" "anthropic_api_key" {
  project   = var.project_id
  secret_id = var.anthropic_secret_name
}

data "google_secret_manager_secret" "gemini_api_key" {
  project   = var.project_id
  secret_id = var.gemini_secret_name
}

data "google_secret_manager_secret" "wandb_api_key" {
  project   = var.project_id
  secret_id = var.wandb_secret_name
}

# Terraform-managed GCS bucket for podcasts
resource "google_storage_bucket" "public_bucket" {
  project  = var.project_id
  name     = var.public_bucket_name
  location = var.region
  labels = {
    project = var.project_id
  }
  force_destroy               = false
  uniform_bucket_level_access = true
}

resource "google_storage_bucket_object" "logo" {
  name         = "assets/logo.webp"
  source       = var.podcast_logo_source
  content_type = "image/webp"
  bucket       = google_storage_bucket.public_bucket.name
}

resource "google_storage_bucket_object" "logo_font" {
  name         = "assets/logo.ttf"
  source       = var.logo_font_source
  content_type = "font/ttf"
  bucket       = google_storage_bucket.public_bucket.name
}

# Terraform-managed GCS bucket for podcast intermediate artifacts
resource "google_storage_bucket" "private_bucket" {
  project  = var.project_id
  name     = var.private_bucket_name
  location = var.region
  labels = {
    project = var.project_id
  }
  force_destroy               = false
  uniform_bucket_level_access = true
}

# Make bucket public
resource "google_storage_bucket_iam_member" "member" {
  provider = google
  bucket   = google_storage_bucket.public_bucket.name
  role     = "roles/storage.objectViewer"
  member   = "allUsers"
}

resource "google_firestore_database" "default" {
  project     = var.project_id
  type        = "FIRESTORE_NATIVE"
  name        = "(default)"
  location_id = var.region
}

resource "google_firestore_index" "repos_last_processed_at_try_count" {
  project    = var.project_id
  collection = "repos"

  fields {
    field_path = "lastProcessedAt"
    order      = "ASCENDING"
  }

  fields {
    field_path = "tryCount"
    order      = "ASCENDING"
  }

  depends_on = [google_firestore_database.default]
}

resource "google_project_iam_member" "podcast_generator_service_sa_firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.podcast_generator_service_sa.email}"
}

resource "google_project_iam_member" "podcast_generator_service_sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.podcast_generator_service_sa.email}"
}

resource "google_cloud_run_service" "web_service" {
  project  = var.project_id
  name     = var.web_service_name
  location = var.region

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "all"
    }
    labels = local.common_labels
  }

  template {
    spec {
      service_account_name = google_service_account.web_service_sa.email
      containers {
        image = var.web_container_image
        env {
          name  = "ENV"
          value = "prod"
        }
        env {
          name  = "PODCAST_GENERATOR_SERVICE_URL"
          value = google_cloud_run_service.podcast_generator_service.status[0].url
        }
        resources {
          limits = {
            memory = "512Mi"
            cpu    = "1"
          }
        }
      }
      timeout_seconds       = 300
      container_concurrency = 80
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_cloud_run_service.podcast_generator_service]
}

resource "google_cloud_run_service_iam_member" "web_invoker" {
  project  = var.project_id
  service  = google_cloud_run_service.web_service.name
  location = google_cloud_run_service.web_service.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

resource "google_cloud_run_service" "podcast_generator_service" {
  project  = var.project_id
  name     = var.podcast_generator_service_name
  location = var.region

  metadata {
    annotations = {
      # FIXME: Figure out how to make podcast generator private
      "run.googleapis.com/ingress" = "all"
    }
    labels = local.common_labels
  }

  template {
    spec {
      service_account_name = google_service_account.podcast_generator_service_sa.email
      containers {
        image = var.podcast_generator_container_image

        env {
          name  = "ENV"
          value = "prod"
        }

        env {
          name  = "GITHUB_APP_CLIENT_ID"
          value = var.github_app_client_id
        }

        env {
          name  = "GITHUB_APP_INSTALLATION_ID"
          value = var.github_app_installation_id
        }

        env {
          name  = "PUBLIC_BUCKET_NAME"
          value = var.public_bucket_name
        }

        env {
          name  = "PRIVATE_BUCKET_NAME"
          value = var.private_bucket_name
        }

        env {
          name  = "TIMEOUT_SECONDS"
          value = var.podcast_generator_service_timeout_seconds
        }

        env {
          name  = "MAX_INSTANCE_REQUEST_CONCURRENCY"
          value = var.podcast_generator_service_concurrency
        }

        env {
          name = "GITHUB_APP_PRIVATE_KEY"
          value_from {
            secret_key_ref {
              name = data.google_secret_manager_secret.github_app_private_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "OPENAI_API_KEY"
          value_from {
            secret_key_ref {
              name = data.google_secret_manager_secret.openai_api_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "ANTHROPIC_API_KEY"
          value_from {
            secret_key_ref {
              name = data.google_secret_manager_secret.anthropic_api_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "GEMINI_API_KEY"
          value_from {
            secret_key_ref {
              name = data.google_secret_manager_secret.gemini_api_key.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name = "WANDB_API_KEY"
          value_from {
            secret_key_ref {
              name = data.google_secret_manager_secret.wandb_api_key.secret_id
              key  = "latest"
            }
          }
        }

        resources {
          limits = {
            memory = "1Gi"
            cpu    = "1"
          }
        }
      }

      timeout_seconds       = var.podcast_generator_service_timeout_seconds
      container_concurrency = var.podcast_generator_service_concurrency
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_storage_bucket.public_bucket, google_storage_bucket.private_bucket]
}

resource "google_cloud_run_service_iam_member" "podcast_generator_invoker" {
  project  = var.project_id
  service  = google_cloud_run_service.podcast_generator_service.name
  location = google_cloud_run_service.podcast_generator_service.location
  role     = "roles/run.invoker"
  # FIXME: Figure out how to make podcast generator private. Will need to
  # allow the web service to invoke it, the scheduler to trigger it, and
  # a way for admins to invoke it for fixing things.
  member = "allUsers"
}

resource "google_storage_bucket_iam_member" "podcast_generator_service_sa_storage_public" {
  bucket = google_storage_bucket.public_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.podcast_generator_service_sa.email}"
}

resource "google_storage_bucket_iam_member" "podcast_generator_service_sa_storage_private" {
  bucket = google_storage_bucket.private_bucket.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.podcast_generator_service_sa.email}"
}

resource "google_project_iam_binding" "podcast_generator_service_sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  members = [
    "serviceAccount:${google_service_account.podcast_generator_service_sa.email}"
  ]
}

resource "google_cloud_scheduler_job" "podcast_update_job" {
  project     = var.project_id
  name        = "pi-dev-podcasts-update-job"
  description = "Triggers the podcasts generation regularly"
  schedule    = var.schedule_cron
  time_zone   = "Etc/UTC"
  region      = var.region

  http_target {
    uri         = "${google_cloud_run_service.podcast_generator_service.status[0].url}/update"
    http_method = "POST"
    oidc_token {
      service_account_email = google_service_account.scheduler_sa.email
      audience              = google_cloud_run_service.podcast_generator_service.status[0].url
    }
  }

  attempt_deadline = "600s"
  retry_config {
    retry_count          = 2
    max_retry_duration   = "3600s"
    min_backoff_duration = "30s"
    max_backoff_duration = "300s"
  }
}

resource "google_monitoring_notification_channel" "email" {
  project      = var.project_id
  display_name = "Email Notification Channel"
  type         = "email"
  labels = {
    email_address = var.alert_email_address
  }
}

resource "google_monitoring_alert_policy" "critical_logs" {
  project      = var.project_id
  display_name = "Critical Logs Alert"
  combiner     = "OR"
  severity     = "CRITICAL"

  conditions {
    display_name = "Log entries with CRITICAL severity"
    condition_matched_log {
      filter = "resource.type=\"cloud_run_revision\" AND severity=CRITICAL"
    }
  }

  notification_channels = [google_monitoring_notification_channel.email.name, var.alert_mobile_name]

  alert_strategy {
    notification_rate_limit {
      period = "3600s" # Limit notifications to once per hour
    }
  }
}

# From https://github.com/terraform-google-modules/terraform-google-lb-http/blob/34c85bb282150233bf9af74862b97942335aa529/examples/cloudrun/main.tf
# [START cloudloadbalancing_ext_http_cloudrun]
# Certificate Manager DNS authorization
resource "google_certificate_manager_dns_authorization" "pi_dev_auth" {
  name        = "pi-dev-dns-auth"
  domain      = var.domain_name
  project     = var.project_id
}

# Certificate Manager certificate using DNS authorization
resource "google_certificate_manager_certificate" "pi_dev_cert" {
  name        = "pi-dev-cert"
  project     = var.project_id
  managed {
    domains = [var.domain_name]
    dns_authorizations = [
      google_certificate_manager_dns_authorization.pi_dev_auth.id
    ]
  }
}

# Certificate Map to link certificates to load balancer
resource "google_certificate_manager_certificate_map" "pi_dev_map" {
  name    = "pi-dev-cert-map"
  project = var.project_id
}

# Certificate Map Entry to specify which certificate to use for which hostname
resource "google_certificate_manager_certificate_map_entry" "pi_dev_map_entry" {
  name         = "primary-entry"
  map          = google_certificate_manager_certificate_map.pi_dev_map.name
  certificates = [google_certificate_manager_certificate.pi_dev_cert.id]
  hostname     = var.domain_name
  project      = var.project_id
}

module "lb-http" {
  source  = "terraform-google-modules/lb-http/google//modules/serverless_negs"
  version = "~> 12.0"

  name    = var.load_balancer_name
  project = var.project_id

  # We still need SSL enabled for the load balancer
  ssl                             = true
  managed_ssl_certificate_domains = [var.domain_name]
  https_redirect                  = true
  certificate_map                 = google_certificate_manager_certificate_map.pi_dev_map.id

  url_map        = google_compute_url_map.load_balancer_url_map.self_link
  create_url_map = false

  backends = {
    default = {
      description = null
      groups = [
        {
          group = google_compute_region_network_endpoint_group.serverless_neg.id
        }
      ]
      enable_cdn = false

      iap_config = {
        enable = false
      }
      log_config = {
        enable = false
      }
    }
  }
}

resource "google_compute_url_map" "load_balancer_url_map" {
  // note that this is the name of the load balancer
  name            = var.load_balancer_name
  default_service = module.lb-http.backend_services["default"].self_link

  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = module.lb-http.backend_services["default"].self_link

    path_rule {
      paths = [
        "/assets",
        "/assets/*",
        "/shows",
        "/shows/*"
      ]
      service = google_compute_backend_bucket.assets.self_link
    }
  }
}

resource "google_compute_backend_bucket" "assets" {
  name        = "assets"
  description = "Contains static resources"
  bucket_name = google_storage_bucket.public_bucket.name
  enable_cdn  = true

  cdn_policy {
    cache_mode         = "USE_ORIGIN_HEADERS"
    request_coalescing = true
  }
}

resource "google_compute_region_network_endpoint_group" "serverless_neg" {
  provider              = google-beta
  name                  = "serverless-neg"
  network_endpoint_type = "SERVERLESS"
  region                = var.region
  cloud_run {
    service = google_cloud_run_service.web_service.name
  }
}
# [END cloudloadbalancing_ext_http_cloudrun]
