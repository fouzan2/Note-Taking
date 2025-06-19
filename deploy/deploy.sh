#!/bin/bash

# Deployment script for Note Taking API to Google Cloud Run
set -e

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | xargs)
fi

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="note-taking-api"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Deploying $SERVICE_NAME to GCP Project: $PROJECT_ID"

# Verify gcloud is configured
echo "Verifying gcloud configuration..."
gcloud config set project $PROJECT_ID

# Get Redis instance IP
echo "Getting Redis instance IP..."
REDIS_HOST=$(gcloud redis instances describe note-taking-redis --region=$REGION --format="value(host)")
echo "Redis host: $REDIS_HOST"

# Build and submit using Cloud Build
echo "Building container image..."
gcloud builds submit \
    --config cloudbuild.yaml \
    --substitutions=_REGION=$REGION,_CLOUD_SQL_INSTANCE=${PROJECT_ID}:${REGION}:note-taking-db

# Get the service account for Cloud Run
SERVICE_ACCOUNT="${PROJECT_ID}-compute@developer.gserviceaccount.com"

# Deploy to Cloud Run with additional configuration
echo "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --platform managed \
    --allow-unauthenticated \
    --service-account $SERVICE_ACCOUNT \
    --add-cloudsql-instances ${PROJECT_ID}:${REGION}:note-taking-db \
    --vpc-connector note-taking-connector \
    --vpc-egress all-traffic \
    --set-env-vars "REDIS_HOST=$REDIS_HOST" \
    --set-secrets "DB_PASSWORD=db-password:latest,SECRET_KEY=jwt-secret:latest,API_KEY=api-key:latest" \
    --max-instances 10 \
    --min-instances 1 \
    --memory 1Gi \
    --cpu 1 \
    --timeout 300 \
    --concurrency 80

# Run database migrations
echo "Running database migrations..."
gcloud run jobs create run-migrations \
    --image ${IMAGE_NAME}:latest \
    --region $REGION \
    --service-account $SERVICE_ACCOUNT \
    --add-cloudsql-instances ${PROJECT_ID}:${REGION}:note-taking-db \
    --vpc-connector note-taking-connector \
    --set-env-vars "REDIS_HOST=$REDIS_HOST" \
    --set-secrets "DB_PASSWORD=db-password:latest" \
    --command "alembic" \
    --args "upgrade,head" \
    --max-retries 1 \
    --wait || echo "Migration job already exists"

# Execute the migration job
gcloud run jobs execute run-migrations --region $REGION --wait

# Get the service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region $REGION --format "value(status.url)")

echo "======================================"
echo "Deployment Complete!"
echo "======================================"
echo "Service URL: $SERVICE_URL"
echo "API Docs: ${SERVICE_URL}/docs"
echo "Health Check: ${SERVICE_URL}/health"
echo ""
echo "To view logs:"
echo "gcloud run services logs read $SERVICE_NAME --region $REGION"
echo "======================================" 