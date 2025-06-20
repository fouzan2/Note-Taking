# GCP Deployment Troubleshooting Guide

This guide helps resolve common issues when deploying the Note Taking API to Google Cloud Platform.

## Common Issues and Solutions

### 1. Artifact Registry Permission Error

**Error:**
```
denied: Permission "artifactregistry.repositories.uploadArtifacts" denied on resource "projects/***/locations/us/repositories/gcr.io"
```

**Solution:**
```bash
# Quick fix - run this script
cd deploy
./update-service-account-permissions.sh

# Or manually:
gcloud services enable artifactregistry.googleapis.com
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

### 2. GitHub Secrets Not Found

**Error:**
```
Error: google-github-actions/auth failed with: the GitHub Action workflow must specify exactly one of "workload_identity_provider" or "credentials_json"!
```

**Solution:**
1. Ensure you've added the secrets to your GitHub repository:
   - Go to Settings → Secrets and variables → Actions
   - Add `GCP_PROJECT_ID` and `GCP_SA_KEY`
2. Make sure the secret names match exactly (case-sensitive)
3. If running from a fork, secrets won't be available

### 3. Cloud SQL Connection Issues

**Error:**
```
Error: failed to connect to `host=xxx user=noteuser database=note_taking_db`: dial error
```

**Solution:**
1. Ensure Cloud SQL Admin API is enabled
2. Check VPC connector is created and healthy
3. Verify the Cloud SQL instance is running
4. Confirm the database user exists

### 4. Redis Connection Failed

**Error:**
```
redis.exceptions.ConnectionError: Error -2 connecting to redis-host:6379
```

**Solution:**
1. Verify Redis instance is created and running
2. Check VPC connector configuration
3. Ensure the Redis host is correctly set in environment variables

### 5. Secret Manager Access Denied

**Error:**
```
Permission 'secretmanager.versions.access' denied on resource
```

**Solution:**
```bash
# Grant secret accessor role to service account
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 6. Cloud Run Deployment Failed

**Error:**
```
ERROR: (gcloud.run.deploy) PERMISSION_DENIED: Permission 'run.services.create' denied
```

**Solution:**
```bash
# Grant Cloud Run admin role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"
```

## Verification Commands

### Check Service Account Permissions
```bash
# List all roles for the service account
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

### Check Enabled APIs
```bash
# List all enabled APIs
gcloud services list --enabled --format="table(name)"
```

### Check Infrastructure Status
```bash
# Cloud SQL
gcloud sql instances describe note-taking-db

# Redis
gcloud redis instances describe note-taking-redis --region=us-central1

# VPC Connector
gcloud compute networks vpc-access connectors describe note-taking-connector --region=us-central1

# Secrets
gcloud secrets list
```

## Complete Verification Script

Run this script to check your entire setup:
```bash
cd deploy
./verify-gcp-setup.sh
```

## Reset and Start Over

If you need to completely reset your service account:

1. Delete the old service account:
```bash
gcloud iam service-accounts delete github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

2. Run the setup script again:
```bash
cd deploy
./setup-gcp-service-account.sh
```

3. Update the GitHub secrets with the new key

## Getting Help

If you're still experiencing issues:

1. Check the GitHub Actions logs for detailed error messages
2. Verify all prerequisites are met using `./verify-gcp-setup.sh`
3. Ensure your GCP project has billing enabled
4. Check that you're not hitting any quotas or limits

## Required IAM Roles Summary

The service account needs these roles:
- `roles/run.admin` - Deploy to Cloud Run
- `roles/storage.admin` - Push images to GCR
- `roles/artifactregistry.writer` - Push images to Artifact Registry
- `roles/cloudsql.client` - Connect to Cloud SQL
- `roles/compute.networkUser` - Use VPC connector
- `roles/secretmanager.secretAccessor` - Access secrets
- `roles/iam.serviceAccountUser` - Act as service account
- `roles/redis.editor` - Access Redis instance 