
terraform {
  backend "gcs" {
    bucket = "PI_DEV_TERRAFORM_STATE_BUCKET"
    prefix = "repo-to-podcast"
  }
}
