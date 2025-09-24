# PI.dev - Repository to Podcast Maintenance Guide

> Placeholder tokens such as `PI_DEV_GCP_PROJECT_ID` mark deployment-specific values you must supply.

## Project Overview

PI.dev (Repository to Podcast) is an AI-powered service that automatically generates podcast episodes about GitHub repositories. The system:

1. Fetches repository data (commits, PRs, issues, discussions) using GitHub's GraphQL API
2. Generates podcast scripts using LLMs (Claude, OpenAI, or Gemini)
3. Converts scripts to audio using text-to-speech
4. Publishes podcast episodes with RSS feeds

## Infrastructure Components

- **Google Cloud Platform**: All services hosted on GCP in the `PI_DEV_GCP_PROJECT_ID` project
  - **Cloud Run**: Hosts both web and podcast generator services
  - **Cloud Storage**: Stores audio files, assets, and metadata
  - **Firestore**: Database for repository processing state
  - **Secret Manager**: Stores API keys for GitHub, LLMs, etc.
  - **Cloud Scheduler**: Triggers regular podcast generation
  - **Load Balancer**: Routes traffic with path-based routing
- **Cloudflare**: DNS management with proxying enabled

## Services

### Web Service (Next.js)

- User-facing interface to submit repository URLs
- Displays repository information and podcast links
- Handles user feedback collection
- Deployed via `./scripts/deploy_web.sh`

### Podcast Generator Service (Python/Flask)

- Fetches repository data using GitHub GraphQL API
- Generates podcast scripts through multi-stage LLM prompting
- Converts scripts to audio and creates RSS feeds
- Deployed via `./scripts/deploy_podcast_generator.sh`

## SSL Certificate Management

The site uses Google Certificate Manager with DNS-based validation for SSL certificates, enabling Cloudflare proxying for security benefits.

### Adding or Updating SSL Certificates

1. SSL configuration is in Terraform under `/terraform/main.tf`
2. After running Terraform, check the DNS validation requirements:

   ```bash
   # Apply Terraform changes
   ./scripts/apply_terraform.sh

   # Check the DNS authorization record output
   cd terraform && terraform output dns_authorization_record
   ```

3. Create/update CNAME record in Cloudflare:
   - Name: The `name` value from output (typically \_acme-challenge.pi.dev)
   - Target: The `value` from output (ending with .acme.googleusercontent.com)
   - Proxy status: **Disabled** (gray cloud) - IMPORTANT!

### Troubleshooting Certificates

If certificate validation fails:

1. Verify CNAME record in Cloudflare matches Terraform output exactly
2. Ensure Cloudflare proxy is disabled for the \_acme-challenge record
3. Check certificate status:
   ```bash
   gcloud certificate-manager certificates describe PI_DEV_CERTIFICATE_NAME --project=PI_DEV_GCP_PROJECT_ID
   ```

## Deployment Process

### Podcast Generator Service

```bash
# Deploy podcast generator
./scripts/deploy_podcast_generator.sh
```

### Web Service

```bash
# Deploy web service
./scripts/deploy_web.sh
```

## Common Maintenance Tasks

### Updating Terraform Infrastructure

```bash
# Apply Terraform changes using the project script
./scripts/apply_terraform.sh
```

### Checking Logs

```bash
# Podcast generator logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=PI_DEV_PODCAST_GENERATOR_SERVICE" --project=PI_DEV_GCP_PROJECT_ID --limit=10

# Web service logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=PI_DEV_WEB_SERVICE" --project=PI_DEV_GCP_PROJECT_ID --limit=10
```

### Storage Management

```bash
# List bucket contents
gsutil ls -l gs://PI_DEV_PUBLIC_BUCKET/

# Public facing assets are in /assets directory
gsutil ls -l gs://PI_DEV_PUBLIC_BUCKET/assets/

# View generated podcast episodes
gsutil ls -l gs://PI_DEV_PUBLIC_BUCKET/shows/
```

### Monitoring and Alerts

- Critical log alerts are configured to notify via email
- Check GCP Monitoring dashboard for service health
- Alert notifications are rate-limited to once per hour
