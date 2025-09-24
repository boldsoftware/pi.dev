#!/usr/bin/env bash
set -euo pipefail

# Hardcode project ID
GCP_PROJECT_ID="${GCP_PROJECT_ID:-PI_DEV_GCP_PROJECT_ID}"
REGION="${REGION:-us-central1}"
CLOUD_RUN_SERVICE_NAME="${CLOUD_RUN_SERVICE_NAME:-pi-dev-web-service}"
CLOUD_RUN_IMAGE="${CLOUD_RUN_IMAGE:-${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/pi-registry/pi-dev-web-image:latest}"

# cd into web directory
cd "$(dirname "${BASH_SOURCE[0]}")/../web"

gcloud builds submit \
	--config=cloudbuild.yaml \
	--project=$GCP_PROJECT_ID \
	--substitutions COMMIT_SHA="$(git rev-parse HEAD)"
gcloud run deploy "$CLOUD_RUN_SERVICE_NAME" \
    --project=$GCP_PROJECT_ID \
    --region "$REGION" \
    --image "$CLOUD_RUN_IMAGE"
