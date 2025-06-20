#!/bin/bash

# Script to verify GCP setup is complete before deployment
# This helps diagnose common setup issues

set -e

echo "🔍 Verifying GCP Setup for Note Taking API Deployment"
echo "===================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if gcloud is installed
echo -n "Checking gcloud CLI... "
if command -v gcloud &> /dev/null; then
    echo -e "${GREEN}✓ Installed${NC}"
    GCLOUD_VERSION=$(gcloud version --format="value(version)")
    echo "  Version: $GCLOUD_VERSION"
else
    echo -e "${RED}✗ Not installed${NC}"
    echo "  Please install gcloud CLI: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if authenticated
echo -n "Checking gcloud authentication... "
if gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    echo -e "${GREEN}✓ Authenticated${NC}"
    echo "  Account: $ACTIVE_ACCOUNT"
else
    echo -e "${RED}✗ Not authenticated${NC}"
    echo "  Run: gcloud auth login"
    exit 1
fi

# Check project
echo -n "Checking project configuration... "
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -n "$PROJECT_ID" ]; then
    echo -e "${GREEN}✓ Project configured${NC}"
    echo "  Project ID: $PROJECT_ID"
else
    echo -e "${RED}✗ No project set${NC}"
    echo "  Run: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

# Check APIs
echo ""
echo "Checking required APIs..."
REQUIRED_APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "sql-component.googleapis.com"
    "sqladmin.googleapis.com"
    "redis.googleapis.com"
    "vpcaccess.googleapis.com"
    "secretmanager.googleapis.com"
    "compute.googleapis.com"
    "servicenetworking.googleapis.com"
)

ALL_APIS_ENABLED=true
for API in "${REQUIRED_APIS[@]}"; do
    echo -n "  $API... "
    if gcloud services list --enabled --filter="name:$API" --format="value(name)" 2>/dev/null | grep -q "$API"; then
        echo -e "${GREEN}✓ Enabled${NC}"
    else
        echo -e "${RED}✗ Not enabled${NC}"
        ALL_APIS_ENABLED=false
    fi
done

if [ "$ALL_APIS_ENABLED" = false ]; then
    echo ""
    echo -e "${YELLOW}To enable all required APIs, run:${NC}"
    echo "gcloud services enable ${REQUIRED_APIS[@]}"
fi

# Check for service account
echo ""
echo -n "Checking for GitHub Actions service account... "
SA_EMAIL="github-actions-deployer@${PROJECT_ID}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe "$SA_EMAIL" &> /dev/null; then
    echo -e "${GREEN}✓ Exists${NC}"
    echo "  Email: $SA_EMAIL"
    
    # Check roles
    echo "  Checking IAM roles..."
    REQUIRED_ROLES=(
        "roles/run.admin"
        "roles/storage.admin"
        "roles/artifactregistry.writer"
        "roles/cloudsql.client"
        "roles/compute.networkUser"
        "roles/secretmanager.secretAccessor"
        "roles/iam.serviceAccountUser"
        "roles/redis.editor"
    )
    
    for ROLE in "${REQUIRED_ROLES[@]}"; do
        echo -n "    $ROLE... "
        if gcloud projects get-iam-policy "$PROJECT_ID" \
            --flatten="bindings[].members" \
            --filter="bindings.role:$ROLE AND bindings.members:serviceAccount:$SA_EMAIL" \
            --format="value(bindings.role)" 2>/dev/null | grep -q "$ROLE"; then
            echo -e "${GREEN}✓${NC}"
        else
            echo -e "${RED}✗${NC}"
        fi
    done
else
    echo -e "${RED}✗ Not found${NC}"
    echo "  Run: ./setup-gcp-service-account.sh"
fi

# Check for infrastructure
echo ""
echo "Checking GCP infrastructure..."

# Check Cloud SQL
echo -n "  Cloud SQL instance (note-taking-db)... "
if gcloud sql instances describe note-taking-db --project="$PROJECT_ID" &> /dev/null; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${YELLOW}○ Not found${NC}"
    echo "    Will be created by setup script"
fi

# Check Redis
echo -n "  Redis instance (note-taking-redis)... "
if gcloud redis instances describe note-taking-redis --region=us-central1 --project="$PROJECT_ID" &> /dev/null; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${YELLOW}○ Not found${NC}"
    echo "    Will be created by setup script"
fi

# Check VPC Connector
echo -n "  VPC Connector (note-taking-connector)... "
if gcloud compute networks vpc-access connectors describe note-taking-connector --region=us-central1 --project="$PROJECT_ID" &> /dev/null; then
    echo -e "${GREEN}✓ Exists${NC}"
else
    echo -e "${YELLOW}○ Not found${NC}"
    echo "    Will be created by setup script"
fi

# Check secrets
echo ""
echo "Checking Secret Manager secrets..."
REQUIRED_SECRETS=("db-password" "jwt-secret" "api-key")
for SECRET in "${REQUIRED_SECRETS[@]}"; do
    echo -n "  $SECRET... "
    if gcloud secrets describe "$SECRET" --project="$PROJECT_ID" &> /dev/null; then
        echo -e "${GREEN}✓ Exists${NC}"
    else
        echo -e "${YELLOW}○ Not found${NC}"
        echo "    Will be created by setup script"
    fi
done

# Summary
echo ""
echo "===================================================="
echo "Summary:"
echo ""

if [ "$ALL_APIS_ENABLED" = true ]; then
    echo -e "${GREEN}✓ All required APIs are enabled${NC}"
else
    echo -e "${RED}✗ Some APIs need to be enabled${NC}"
fi

echo ""
echo "Next steps:"
echo "1. If any APIs are disabled, enable them with the command shown above"
echo "2. If the service account doesn't exist, run: ./setup-gcp-service-account.sh"
echo "3. Add the GitHub secrets (GCP_PROJECT_ID and GCP_SA_KEY) to your repository"
echo "4. Run infrastructure setup: ./setup-gcp.sh"
echo "5. Deploy with GitHub Actions or run: ./deploy.sh"
echo ""
echo "For detailed instructions, see: GITHUB_SECRETS_SETUP.md" 