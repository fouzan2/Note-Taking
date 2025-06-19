#!/bin/bash

# GCP Infrastructure Setup Script for Note Taking API
# This script sets up the necessary GCP resources for production deployment

set -e

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
ZONE=${ZONE:-"us-central1-a"}
SERVICE_NAME="note-taking-api"
DB_INSTANCE_NAME="note-taking-db"
REDIS_INSTANCE_NAME="note-taking-redis"
VPC_CONNECTOR_NAME="note-taking-connector"

echo "Setting up GCP infrastructure for $SERVICE_NAME in project $PROJECT_ID"

# Enable required APIs
echo "Enabling required GCP APIs..."
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    sqladmin.googleapis.com \
    redis.googleapis.com \
    secretmanager.googleapis.com \
    vpcaccess.googleapis.com \
    servicenetworking.googleapis.com \
    cloudresourcemanager.googleapis.com

# Create VPC connector for private communication
echo "Creating VPC connector..."
gcloud compute networks vpc-access connectors create $VPC_CONNECTOR_NAME \
    --region=$REGION \
    --subnet-mode=auto \
    --min-instances=2 \
    --max-instances=10 \
    --machine-type=e2-micro || echo "VPC connector already exists"

# Create Cloud SQL PostgreSQL instance
echo "Creating Cloud SQL PostgreSQL instance..."
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-g1-small \
    --region=$REGION \
    --network=default \
    --no-assign-ip \
    --database-flags=max_connections=100 || echo "Cloud SQL instance already exists"

# Create database and user
echo "Creating database..."
gcloud sql databases create note_taking_db \
    --instance=$DB_INSTANCE_NAME || echo "Database already exists"

# Generate secure password
DB_PASSWORD=$(openssl rand -base64 32)

# Create database user
echo "Creating database user..."
gcloud sql users create noteuser \
    --instance=$DB_INSTANCE_NAME \
    --password=$DB_PASSWORD || echo "User already exists"

# Create Redis instance (Memorystore)
echo "Creating Redis instance..."
gcloud redis instances create $REDIS_INSTANCE_NAME \
    --size=1 \
    --region=$REGION \
    --redis-version=redis_7_0 \
    --network=default || echo "Redis instance already exists"

# Store secrets in Secret Manager
echo "Storing secrets in Secret Manager..."

# Database password
echo -n "$DB_PASSWORD" | gcloud secrets create db-password \
    --data-file=- || echo -n "$DB_PASSWORD" | gcloud secrets versions add db-password --data-file=-

# Generate and store JWT secret
JWT_SECRET=$(openssl rand -base64 64)
echo -n "$JWT_SECRET" | gcloud secrets create jwt-secret \
    --data-file=- || echo -n "$JWT_SECRET" | gcloud secrets versions add jwt-secret --data-file=-

# Generate and store other secrets
API_KEY=$(openssl rand -base64 32)
echo -n "$API_KEY" | gcloud secrets create api-key \
    --data-file=- || echo -n "$API_KEY" | gcloud secrets versions add api-key --data-file=-

# Grant Cloud Run service account access to secrets
echo "Granting secret access to Cloud Run..."
SERVICE_ACCOUNT="${PROJECT_ID}-compute@developer.gserviceaccount.com"

for secret in db-password jwt-secret api-key; do
    gcloud secrets add-iam-policy-binding $secret \
        --member="serviceAccount:$SERVICE_ACCOUNT" \
        --role="roles/secretmanager.secretAccessor"
done

# Create Cloud Storage bucket for backups (optional)
echo "Creating backup bucket..."
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://${PROJECT_ID}-note-taking-backups/ || echo "Bucket already exists"

# Output connection details
echo "======================================"
echo "GCP Infrastructure Setup Complete!"
echo "======================================"
echo "Project ID: $PROJECT_ID"
echo "Region: $REGION"
echo "Cloud SQL Instance: $DB_INSTANCE_NAME"
echo "Redis Instance: $REDIS_INSTANCE_NAME"
echo "VPC Connector: $VPC_CONNECTOR_NAME"
echo ""
echo "Next steps:"
echo "1. Update .env.production with the connection details"
echo "2. Run database migrations"
echo "3. Deploy using Cloud Build: gcloud builds submit --config cloudbuild.yaml"
echo "======================================" 