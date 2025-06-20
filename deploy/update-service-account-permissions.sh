#!/bin/bash

# This script updates an existing service account with missing permissions
# Use this if you're getting permission errors when pushing to GCR

set -e

# Configuration
PROJECT_ID=$(gcloud config get-value project)
SERVICE_ACCOUNT_NAME="github-actions-deployer"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Updating service account permissions for project: ${PROJECT_ID}"

# Check if service account exists
if ! gcloud iam service-accounts describe "$SERVICE_ACCOUNT_EMAIL" &> /dev/null; then
    echo "Error: Service account ${SERVICE_ACCOUNT_EMAIL} does not exist!"
    echo "Please run ./setup-gcp-service-account.sh first"
    exit 1
fi

# Enable Artifact Registry API if not already enabled
echo "Ensuring Artifact Registry API is enabled..."
gcloud services enable artifactregistry.googleapis.com

# Grant Artifact Registry Writer role
echo "Granting artifactregistry.writer role..."
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="roles/artifactregistry.writer" \
    --quiet

echo ""
echo "✅ Service account permissions updated!"
echo ""
echo "The service account now has permission to push images to GCR/Artifact Registry."
echo ""
echo "If you're still experiencing issues:"
echo "1. Ensure you've updated the GCP_SA_KEY secret in GitHub with a fresh key"
echo "2. Re-run your GitHub Actions workflow"
echo ""
echo "To create a new key (if needed):"
echo "  gcloud iam service-accounts keys create new-key.json --iam-account=${SERVICE_ACCOUNT_EMAIL}" 