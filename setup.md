### Detailed Setup Instructions

> Placeholder tokens like `PI_DEV_GCP_PROJECT_ID` and `PI_DEV_TERRAFORM_STATE_BUCKET` represent values you need to provide for your environment.

1. **Create a GCP Project & Enable APIs**

   First, create the `PI_DEV_GCP_PROJECT_ID` project using [Google console](https://console.cloud.google.com) and enable billing. Then run the following commands:

   ```bash
   gcloud config set project ${PI_DEV_GCP_PROJECT_ID}
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com containerregistry.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com cloudscheduler.googleapis.com iam.googleapis.com firestore.googleapis.com compute.googleapis.com
   ```

2. **Create and install a GitHub App**

   - **Create the GitHub App**:

     1. Go to your GitHub Settings -> Developer settings -> GitHub Apps.
     2. Click "New GitHub App".
     3. Fill in the required details (Name, Homepage URL can be something placeholder, etc.).
     4. Select private
     5. Save the app. You will see a **Client ID**.
     6. Generate a private key for the app and download it.

   - **Install the GitHub App on a repository**:
     - Go to the newly created app’s page.
     - Click "Install App" and install it on your organization.
     - The installation ID will be the last part of the URL

   At this point, you have three essential pieces of information:

   - **APP_ID**: e.g. `123456`
   - **INSTALLATION_ID**: e.g. `9876543`
   - **PRIVATE_KEY**: The contents of the downloaded `.pem` file

3. **Add Github app info to apply script**

   Edit `scripts/apply_terraform.sh` and replace `GITHUB_APP_CLIENT_ID` and `GITHUB_APP_INSTALLATION_ID` with the actual values from above.

4. **Create a GCS Bucket for Terraform State**

   ```bash
   gsutil mb -p ${PI_DEV_GCP_PROJECT_ID} -l us-central1 gs://${PI_DEV_TERRAFORM_STATE_BUCKET}/
   ```

5. **Create and Upload Secrets to Secret Manager**

   ```bash
   gcloud secrets create github_app_private_key --replication-policy=automatic
   gcloud secrets versions add github_app_private_key --data-file ./path/to/github_key

   gcloud secrets create openai_api_key --replication-policy=automatic
   gcloud secrets versions add openai_api_key --data-file ./path/to/openai_key

   gcloud secrets create anthropic_api_key --replication-policy=automatic
   gcloud secrets versions add anthropic_api_key --data-file ./path/to/anthropic_key

   gcloud secrets create gemini_api_key --replication-policy=automatic
   gcloud secrets versions add gemini_api_key --data-file ./path/to/gemini_key

   gcloud secrets create wandb_api_key --replication-policy=automatic
   gcloud secrets versions add wandb_api_key --data-file ./path/to/wandb_key
   ```

6. **Apply Terraform Infrastructure**

   ```bash
   ./scripts/apply_terraform.sh --init
   ```

   This will initialize Terraform with the GCS backend and apply the infrastructure changes. Note that it uses dummy images for the service, to avoid chicken-egg problem where we can't build images without terraform creating the image registry, but can't create the service without the images. We will replace these dummy images with real images in the next step.

   If you need to make changes to terraform later and then reapply, you can run `./scripts/apply_terraform.sh` without the `--init` flag.

7. **Manually push images**

   ```sh
   GCP_PROJECT_ID=${PI_DEV_GCP_PROJECT_ID} ./scripts/deploy_podcast_generator.sh
   GCP_PROJECT_ID=${PI_DEV_GCP_PROJECT_ID} ./scripts/deploy_web.sh
   ```

   Note that in the future this will be done by the CI/CD pipeline on merge to main.

8. **Add CI/CD Service Account secret to GitHub for CD**

   Export a JSON key and save as a GitHub Secret:

   ```bash
   gcloud iam service-accounts keys create key.json \
     --iam-account=pi-dev-ci-cd@${PI_DEV_GCP_PROJECT_ID}.iam.gserviceaccount.com
   ```

   In GitHub repo settings, add `GCP_SERVICE_ACCOUNT_KEY` secret to production environment with `key.json` content as a single line.

9. **Verification**
   - Run `(cd terraform && terraform output)` to get service URLs.
   - Access the web URL from the output and verify that the web service is running.
   - Access `https://${PI_DEV_WEB_HOST}/github.com/golang/go` to verify the RSS feed is generated, then wait an hour and see if a podcast episode was generated.
