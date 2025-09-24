variable "project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "region" {
  type        = string
  description = "GCP Region for resources"
  default     = "us-central1"
}

variable "domain_name" {
  type        = string
  description = "Domain name for the web service"
  default     = "pi.dev"
}

variable "web_service_name" {
  type    = string
  default = "pi-dev-web-service"
}

variable "load_balancer_name" {
  type    = string
  default = "pi-dev-load-balancer"
}

variable "podcast_logo_source" {
  type        = string
  description = "Local path to the podcast logo"
}

variable "logo_font_source" {
  type        = string
  description = "Local path to the font used to add text to the podcast logo"
}

variable "podcast_generator_service_name" {
  type    = string
  default = "pi-dev-podcast-generator-service"
}

variable "podcast_generator_service_concurrency" {
  type        = number
  description = "Maximum number of concurrent requests for the podcast generator service"
  default     = 16
}

variable "alert_mobile_name" {
  type        = string
  description = "Name of the mobile notification channel for Google Monitoring"
}

variable "web_container_image" {
  type        = string
  description = "Container image for web service"
}

variable "podcast_generator_container_image" {
  type        = string
  description = "Container image for podcast generator service"
}

variable "public_bucket_name" {
  type        = string
  description = "GCS bucket name for podcast outputs"
}

variable "private_bucket_name" {
  type        = string
  description = "GCS bucket name for intermediate artifacts"
}

variable "schedule_cron" {
  type        = string
  description = "CRON schedule for the podcast generator update job"
  default     = "*/5 * * * *"
}

variable "service_account_id" {
  type    = string
  default = "scheduler-invoker"
}

variable "github_secret_name" {
  type    = string
  default = "github_app_private_key"
}

variable "github_app_client_id" {
  type        = string
  description = "GitHub App client ID"
}

variable "github_app_installation_id" {
  type        = string
  description = "GitHub App installation ID"
}

variable "podcast_generator_service_timeout_seconds" {
  type        = number
  description = "Timeout in seconds for the podcast generator service"
  default     = 1800
}

variable "open_ai_secret_name" {
  type    = string
  default = "openai_api_key"
}

variable "anthropic_secret_name" {
  type    = string
  default = "anthropic_api_key"
}

variable "gemini_secret_name" {
  type    = string
  default = "gemini_api_key"
}

variable "wandb_secret_name" {
  type    = string
  default = "wandb_api_key"
}

variable "alert_email_address" {
  type        = string
  description = "Email address to send alerts to"
}
