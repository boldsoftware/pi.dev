#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-PI_DEV_GCP_PROJECT_ID}"
GITHUB_APP_CLIENT_ID="${GITHUB_APP_CLIENT_ID:-PI_DEV_GITHUB_APP_CLIENT_ID}"
GITHUB_APP_INSTALLATION_ID="${GITHUB_APP_INSTALLATION_ID:-PI_DEV_GITHUB_APP_INSTALLATION_ID}"
ALERT_EMAIL_ADDRESS="${ALERT_EMAIL_ADDRESS:-PI_DEV_ALERT_EMAIL}"

# FIXME: It would be better to create the mobile alerting channel from terraform
# but that doesn't seem to be supported by the google cloud beta api at this point
ALERT_MOBILE_NAME="${ALERT_MOBILE_NAME:-PI_DEV_ALERT_MOBILE_CHANNEL}"

if [[ "$*" == *"--init"* ]]; then
	WEB_IMAGE="${WEB_IMAGE:-us-docker.pkg.dev/cloudrun/container/hello}"
	PODCAST_GENERATOR_IMAGE="${PODCAST_GENERATOR_IMAGE:-us-docker.pkg.dev/cloudrun/container/hello}"
else
	WEB_IMAGE="${WEB_IMAGE:-us-central1-docker.pkg.dev/${PROJECT_ID}/pi-registry/pi-dev-web-image:latest}"
	PODCAST_GENERATOR_IMAGE="${PODCAST_GENERATOR_IMAGE:-us-central1-docker.pkg.dev/${PROJECT_ID}/pi-registry/pi-dev-podcast-generator-image:latest}"
fi

PUBLIC_BUCKET_NAME="${PUBLIC_BUCKET_NAME:-${PROJECT_ID}-podcasts-bucket}"
PRIVATE_BUCKET_NAME="${PRIVATE_BUCKET_NAME:-${PROJECT_ID}-podcasts-bucket-private}"
REGION="us-central1"

cd terraform

PODCAST_LOGO_SOURCE="../podcast-generator/images/logo.webp"
LOGO_FONT_SOURCE="../podcast-generator/fonts/Montserrat-VariableFont_wght.ttf"

terraform init

terraform apply \
	-var "project_id=${PROJECT_ID}" \
	-var "github_app_client_id=${GITHUB_APP_CLIENT_ID}" \
	-var "github_app_installation_id=${GITHUB_APP_INSTALLATION_ID}" \
	-var "web_container_image=${WEB_IMAGE}" \
	-var "podcast_generator_container_image=${PODCAST_GENERATOR_IMAGE}" \
	-var "public_bucket_name=${PUBLIC_BUCKET_NAME}" \
	-var "private_bucket_name=${PRIVATE_BUCKET_NAME}" \
	-var "podcast_logo_source=${PODCAST_LOGO_SOURCE}" \
	-var "logo_font_source=${LOGO_FONT_SOURCE}" \
	-var "alert_email_address=${ALERT_EMAIL_ADDRESS}" \
	-var "alert_mobile_name=${ALERT_MOBILE_NAME}" \
	-var "region=${REGION}"
