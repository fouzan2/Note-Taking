#!/bin/bash

# This script creates a service account for GitHub Actions deployment
# Run this from Google Cloud Shell or with gcloud CLI configured

set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT_NAME="github-actions-deployer"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Setting up service account for project: ${PROJECT_ID}"

# Create service account
echo "Creating service account..."
gcloud iam service-accounts create ${SERVICE_ACCOUNT_NAME} \
    --display-name="GitHub Actions Deployer" \
    --description="Service account for GitHub Actions to deploy to Cloud Run" \
    2>/dev/null || echo "Service account already exists"

# Grant necessary roles
echo "Granting IAM roles..."
ROLES=(
    "roles/run.admin"                    # Deploy to Cloud Run
    "roles/storage.admin"                # Push images to GCR
    "roles/artifactregistry.writer"      # Push images to Artifact Registry (used by GCR)
    "roles/cloudsql.client"              # Connect to Cloud SQL
    "roles/compute.networkUser"          # Use VPC connector
    "roles/secretmanager.secretAccessor" # Access secrets
    "roles/iam.serviceAccountUser"       # Act as service account
    "roles/redis.editor"                 # Access Redis instance
)

for ROLE in "${ROLES[@]}"; do
    echo "  Granting ${ROLE}..."
    gcloud projects add-iam-policy-binding ${PROJECT_ID} \
        --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
        --role="${ROLE}" \
        --quiet
done

# Create and download key
echo "Creating service account key..."
KEY_FILE="github-actions-key.json"
gcloud iam service-accounts keys create ${KEY_FILE} \
    --iam-account=${SERVICE_ACCOUNT_EMAIL}

echo ""
echo "✅ Service account setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy the contents of ${KEY_FILE}"
echo "2. Go to your GitHub repository settings"
echo "3. Navigate to Settings > Secrets and variables > Actions"
echo "4. Create these secrets:"
echo "   - GCP_PROJECT_ID: ${PROJECT_ID}"
echo "   - GCP_SA_KEY: (paste the entire contents of ${KEY_FILE})"
echo ""
echo "⚠️  IMPORTANT: Delete ${KEY_FILE} after copying its contents!"
echo "   rm ${KEY_FILE}" 