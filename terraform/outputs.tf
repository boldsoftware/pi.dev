
output "load-balancer-ip" {
  description = "The IP address of the load balancer"
  value       = module.lb-http.external_ip
}

output "podcast_generator_service_url" {
  description = "URL of the podcast generator service"
  value       = google_cloud_run_service.podcast_generator_service.status[0].url
}

output "ci_cd_service_account_email" {
  description = "Email of the ci-cd service account"
  value       = google_service_account.ci_cd_sa.email
}

output "dns_authorization_record" {
  description = "DNS record to create in Cloudflare to validate domain ownership"
  value = {
    name  = google_certificate_manager_dns_authorization.pi_dev_auth.dns_resource_record[0].name
    type  = google_certificate_manager_dns_authorization.pi_dev_auth.dns_resource_record[0].type
    value = google_certificate_manager_dns_authorization.pi_dev_auth.dns_resource_record[0].data
  }
}
