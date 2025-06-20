# GitHub Secrets Setup for GCP Deployment

This guide walks you through setting up the required GitHub secrets for deploying the Note Taking API to Google Cloud Run.

## Prerequisites

1. A Google Cloud Project with billing enabled
2. `gcloud` CLI installed and authenticated
3. Admin access to your GitHub repository

## Required Secrets

The GitHub Actions workflow requires the following secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `GCP_PROJECT_ID` | Your Google Cloud Project ID | `my-project-123456` |
| `GCP_SA_KEY` | Service Account JSON key for authentication | `{...}` (entire JSON content) |

## Step-by-Step Setup

### 1. Set up Google Cloud Resources

First, ensure you have the following GCP services enabled:

```bash
# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  vpcaccess.googleapis.com \
  secretmanager.googleapis.com \
  compute.googleapis.com \
  servicenetworking.googleapis.com
```

### 2. Create Service Account

Run the provided setup script:

```bash
cd deploy
./setup-gcp-service-account.sh
```

This script will:
- Create a service account named `github-actions-deployer`
- Grant all necessary IAM roles
- Generate a JSON key file
- Display your project ID

### 3. Add Secrets to GitHub

1. Go to your GitHub repository
2. Click on **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

#### Add GCP_PROJECT_ID:
- **Name**: `GCP_PROJECT_ID`
- **Value**: Your GCP project ID (shown by the setup script)

#### Add GCP_SA_KEY:
1. Open the `github-actions-key.json` file created by the script
2. Copy the **entire contents** of the file
3. Create a new secret:
   - **Name**: `GCP_SA_KEY`
   - **Value**: Paste the entire JSON content

### 4. Additional Secrets (if not using Secret Manager)

If you're not using Google Secret Manager, you'll also need these secrets:

| Secret Name | Description | How to Generate |
|------------|-------------|-----------------|
| `DB_PASSWORD` | PostgreSQL password | Use a strong password generator |
| `JWT_SECRET` | JWT signing secret | `openssl rand -hex 32` |
| `API_KEY` | API authentication key | `openssl rand -hex 32` |

### 5. Clean Up

**IMPORTANT**: Delete the service account key file after adding it to GitHub:

```bash
rm github-actions-key.json
```

## Troubleshooting

### Secret Not Found Error

If you see an error like `PROJECT_ID:` (empty), ensure:
1. The secret name matches exactly (case-sensitive)
2. The secret is added to the correct repository
3. You're not running from a fork (secrets aren't available in forks)

### Permission Denied Errors

If deployment fails with permission errors:
1. Ensure all required APIs are enabled
2. Check that the service account has all necessary roles
3. Verify the service account key is valid

### Debugging Tips

1. Check if secrets are available by adding a debug step:
   ```yaml
   - name: Debug Secrets
     run: |
       echo "Project ID exists: ${{ secrets.GCP_PROJECT_ID != '' }}"
       echo "SA Key exists: ${{ secrets.GCP_SA_KEY != '' }}"
   ```

2. Verify service account permissions:
   ```bash
   gcloud projects get-iam-policy YOUR_PROJECT_ID \
     --flatten="bindings[].members" \
     --filter="bindings.members:serviceAccount:github-actions-deployer@YOUR_PROJECT_ID.iam.gserviceaccount.com"
   ```

## Security Best Practices

1. **Never commit secrets to the repository**
2. **Rotate service account keys regularly**
3. **Use least privilege principle** - only grant necessary permissions
4. **Monitor service account usage** in GCP IAM logs
5. **Use Secret Manager** for runtime secrets instead of environment variables

## Alternative: Workload Identity Federation

For enhanced security, consider using Workload Identity Federation instead of service account keys:

```yaml
- uses: google-github-actions/auth@v2
  with:
    workload_identity_provider: 'projects/123456789/locations/global/workloadIdentityPools/github/providers/my-repo'
    service_account: 'github-actions@my-project.iam.gserviceaccount.com'
```

This eliminates the need for long-lived service account keys. 