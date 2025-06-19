# Google Cloud Platform Deployment Guide

This guide explains how to deploy the Note Taking API to Google Cloud Platform (GCP) using Cloud Run, Cloud SQL, and Memorystore Redis.

## Prerequisites

1. **Google Cloud Account**: Create a GCP account and project
2. **gcloud CLI**: Install the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
3. **Docker**: Install Docker for local testing
4. **Enable billing**: Ensure billing is enabled for your GCP project

## Initial Setup

1. **Authenticate with GCP**:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. **Set environment variables**:
   ```bash
   export PROJECT_ID=your-gcp-project-id
   export REGION=us-central1
   ```

## Infrastructure Setup

### Automated Setup

Run the setup script to create all required GCP resources:

```bash
cd deploy
chmod +x setup-gcp.sh
./setup-gcp.sh
```

This script will:
- Enable required GCP APIs
- Create a VPC connector for private networking
- Set up Cloud SQL PostgreSQL instance
- Create a Redis instance (Memorystore)
- Store secrets in Secret Manager
- Create a backup bucket

### Manual Setup (Alternative)

If you prefer manual setup:

1. **Enable APIs**:
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
     sqladmin.googleapis.com redis.googleapis.com secretmanager.googleapis.com
   ```

2. **Create Cloud SQL instance**:
   ```bash
   gcloud sql instances create note-taking-db \
     --database-version=POSTGRES_15 \
     --tier=db-g1-small \
     --region=$REGION
   ```

3. **Create Redis instance**:
   ```bash
   gcloud redis instances create note-taking-redis \
     --size=1 --region=$REGION --redis-version=redis_7_0
   ```

## Deployment

### First-Time Deployment

1. **Copy and update environment configuration**:
   ```bash
   cp deploy/env.production.example .env.production
   # Edit .env.production with your values
   ```

2. **Build and deploy**:
   ```bash
   cd deploy
   chmod +x deploy.sh
   ./deploy.sh
   ```

### Using Cloud Build (Recommended)

Deploy directly using Cloud Build:

```bash
gcloud builds submit --config cloudbuild.yaml
```

### Manual Deployment

1. **Build the production image**:
   ```bash
   docker build -f Dockerfile.production -t gcr.io/$PROJECT_ID/note-taking-api:latest .
   ```

2. **Push to Container Registry**:
   ```bash
   docker push gcr.io/$PROJECT_ID/note-taking-api:latest
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy note-taking-api \
     --image gcr.io/$PROJECT_ID/note-taking-api:latest \
     --region $REGION \
     --add-cloudsql-instances $PROJECT_ID:$REGION:note-taking-db \
     --set-secrets "DB_PASSWORD=db-password:latest,SECRET_KEY=jwt-secret:latest"
   ```

## CI/CD with GitHub Actions

1. **Create a service account** for GitHub Actions:
   ```bash
   gcloud iam service-accounts create github-actions \
     --display-name="GitHub Actions Deploy"
   
   # Grant necessary permissions
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/run.admin"
   
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   
   gcloud projects add-iam-policy-binding $PROJECT_ID \
     --member="serviceAccount:github-actions@$PROJECT_ID.iam.gserviceaccount.com" \
     --role="roles/cloudsql.client"
   ```

2. **Create and download service account key**:
   ```bash
   gcloud iam service-accounts keys create github-sa-key.json \
     --iam-account=github-actions@$PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Add GitHub secrets**:
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_SA_KEY`: Contents of `github-sa-key.json`

4. **Push to main branch** to trigger automatic deployment

## Database Migrations

Migrations are automatically run during deployment. To run manually:

```bash
gcloud run jobs execute run-migrations --region $REGION
```

## Monitoring & Logs

### View application logs:
```bash
gcloud run services logs read note-taking-api --region $REGION
```

### View real-time logs:
```bash
gcloud run services logs tail note-taking-api --region $REGION
```

### Access metrics:
- Go to [Cloud Run Console](https://console.cloud.google.com/run)
- Select your service
- View metrics, logs, and traces

## Security Best Practices

1. **Secrets Management**:
   - All sensitive data is stored in Secret Manager
   - Never commit secrets to version control
   - Rotate secrets regularly

2. **Network Security**:
   - Use VPC connector for private communication
   - Cloud SQL uses private IP only
   - Redis is only accessible within VPC

3. **Access Control**:
   - Use service accounts with minimal permissions
   - Enable Cloud IAM for fine-grained access control
   - Review and audit permissions regularly

## Scaling Configuration

The deployment is configured with:
- **Min instances**: 1 (always warm)
- **Max instances**: 10 (auto-scales based on load)
- **Memory**: 1Gi per instance
- **CPU**: 1 vCPU per instance
- **Concurrency**: 80 requests per instance

Adjust these in `cloudbuild.yaml` or deployment scripts as needed.

## Cost Optimization

1. **Cloud Run**: Pay only for actual usage (requests)
2. **Cloud SQL**: Use smallest tier that meets your needs
3. **Redis**: 1GB instance is sufficient for most use cases
4. **Set up budget alerts** in GCP Console

## Troubleshooting

### Common Issues

1. **Database connection errors**:
   - Ensure Cloud SQL Admin API is enabled
   - Check VPC connector configuration
   - Verify database credentials in Secret Manager

2. **Redis connection errors**:
   - Ensure Redis host IP is correctly set
   - Check VPC connector is attached to Cloud Run service

3. **Permission errors**:
   - Verify service account has necessary roles
   - Check Secret Manager permissions

### Debug Commands

```bash
# Check service status
gcloud run services describe note-taking-api --region $REGION

# View Cloud SQL connections
gcloud sql instances describe note-taking-db

# Check Redis instance
gcloud redis instances describe note-taking-redis --region $REGION

# List secrets
gcloud secrets list
```

## Rollback

To rollback to a previous version:

```bash
# List all revisions
gcloud run revisions list --service note-taking-api --region $REGION

# Route traffic to previous revision
gcloud run services update-traffic note-taking-api \
  --to-revisions REVISION_NAME=100 --region $REGION
```

## Cleanup

To remove all resources and avoid charges:

```bash
# Delete Cloud Run service
gcloud run services delete note-taking-api --region $REGION

# Delete Cloud SQL instance
gcloud sql instances delete note-taking-db

# Delete Redis instance
gcloud redis instances delete note-taking-redis --region $REGION

# Delete secrets
gcloud secrets delete db-password
gcloud secrets delete jwt-secret
gcloud secrets delete api-key

# Delete VPC connector
gcloud compute networks vpc-access connectors delete note-taking-connector --region $REGION
```

## Support

For issues or questions:
1. Check Cloud Run logs for errors
2. Review this documentation
3. Check GCP service status
4. Contact your DevOps team 