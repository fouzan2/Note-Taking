#!/bin/bash

# GCP SSH Setup Script
# This script helps set up SSH access to Google Cloud Compute Engine instances

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration - update these values
PROJECT_ID="${PROJECT_ID:-your-project-id}"
INSTANCE_NAME="${INSTANCE_NAME:-note-taking-dev}"
ZONE="${ZONE:-us-central1-a}"
REGION="${REGION:-us-central1}"
USERNAME="${USERNAME:-$(whoami)}"

echo -e "${GREEN}GCP SSH Access Setup Script${NC}"
echo "==============================="
echo "Project ID: $PROJECT_ID"
echo "Instance Name: $INSTANCE_NAME"
echo "Zone: $ZONE"
echo "Username: $USERNAME"
echo ""

# Function to check if gcloud is installed
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        echo -e "${RED}gcloud CLI is not installed!${NC}"
        echo "Please install it from: https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
}

# Function to authenticate with GCP
setup_gcp_auth() {
    echo -e "${YELLOW}Setting up GCP authentication...${NC}"
    
    # Check if already authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        echo -e "${GREEN}Already authenticated with GCP${NC}"
    else
        echo "Please authenticate with GCP:"
        gcloud auth login
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    echo -e "${GREEN}Project set to: $PROJECT_ID${NC}"
}

# Function to create a new VM instance (if needed)
create_vm_instance() {
    echo -e "${YELLOW}Checking if instance exists...${NC}"
    
    if gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE &>/dev/null; then
        echo -e "${GREEN}Instance $INSTANCE_NAME already exists${NC}"
    else
        echo -e "${YELLOW}Creating new VM instance...${NC}"
        gcloud compute instances create $INSTANCE_NAME \
            --zone=$ZONE \
            --machine-type=e2-medium \
            --network-interface=network-tier=STANDARD,subnet=default \
            --maintenance-policy=MIGRATE \
            --provisioning-model=STANDARD \
            --tags=http-server,https-server \
            --create-disk=auto-delete=yes,boot=yes,device-name=$INSTANCE_NAME,image-project=ubuntu-os-cloud,image-family=ubuntu-2204-lts,mode=rw,size=20,type=pd-standard \
            --no-shielded-secure-boot \
            --shielded-vtpm \
            --shielded-integrity-monitoring \
            --reservation-affinity=any
        
        echo -e "${GREEN}Instance created successfully${NC}"
        
        # Wait for instance to be ready
        echo "Waiting for instance to be ready..."
        sleep 30
    fi
}

# Function to set up SSH keys
setup_ssh_keys() {
    echo -e "${YELLOW}Setting up SSH keys...${NC}"
    
    # Generate SSH key if it doesn't exist
    SSH_KEY_PATH="$HOME/.ssh/gcp_compute_engine"
    if [ ! -f "$SSH_KEY_PATH" ]; then
        echo "Generating new SSH key..."
        ssh-keygen -t rsa -b 4096 -f "$SSH_KEY_PATH" -C "$USERNAME@gcp" -N ""
        echo -e "${GREEN}SSH key generated at: $SSH_KEY_PATH${NC}"
    else
        echo -e "${GREEN}SSH key already exists at: $SSH_KEY_PATH${NC}"
    fi
    
    # Add SSH key to project metadata
    echo "Adding SSH key to project metadata..."
    gcloud compute project-info add-metadata \
        --metadata-from-file ssh-keys=<(echo "$USERNAME:$(cat $SSH_KEY_PATH.pub)")
    
    echo -e "${GREEN}SSH key added to project${NC}"
}

# Function to configure firewall rules
setup_firewall_rules() {
    echo -e "${YELLOW}Setting up firewall rules...${NC}"
    
    # Check if SSH firewall rule exists
    if gcloud compute firewall-rules describe default-allow-ssh &>/dev/null; then
        echo -e "${GREEN}SSH firewall rule already exists${NC}"
    else
        echo "Creating SSH firewall rule..."
        gcloud compute firewall-rules create default-allow-ssh \
            --allow tcp:22 \
            --source-ranges 0.0.0.0/0 \
            --description "Allow SSH from anywhere"
        echo -e "${GREEN}SSH firewall rule created${NC}"
    fi
}

# Function to display SSH connection options
show_connection_methods() {
    echo -e "\n${GREEN}=== SSH Connection Methods ===${NC}\n"
    
    # Get instance external IP
    EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
        --zone=$ZONE \
        --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
    
    echo -e "${YELLOW}Method 1: Using gcloud compute ssh (Recommended)${NC}"
    echo "This method handles authentication automatically:"
    echo -e "${GREEN}gcloud compute ssh $INSTANCE_NAME --zone=$ZONE${NC}"
    echo ""
    
    echo -e "${YELLOW}Method 2: Using gcloud with specific user${NC}"
    echo -e "${GREEN}gcloud compute ssh $USERNAME@$INSTANCE_NAME --zone=$ZONE${NC}"
    echo ""
    
    echo -e "${YELLOW}Method 3: Using standard SSH with external IP${NC}"
    echo "First, configure your SSH client (~/.ssh/config):"
    echo -e "${GREEN}cat >> ~/.ssh/config << EOF
Host gcp-$INSTANCE_NAME
    HostName $EXTERNAL_IP
    User $USERNAME
    IdentityFile ~/.ssh/gcp_compute_engine
    StrictHostKeyChecking no
EOF${NC}"
    echo ""
    echo "Then connect using:"
    echo -e "${GREEN}ssh gcp-$INSTANCE_NAME${NC}"
    echo ""
    
    echo -e "${YELLOW}Method 4: Direct SSH command${NC}"
    echo -e "${GREEN}ssh -i ~/.ssh/gcp_compute_engine $USERNAME@$EXTERNAL_IP${NC}"
    echo ""
    
    echo -e "${YELLOW}Method 5: Using IAP (Identity-Aware Proxy) tunnel${NC}"
    echo "More secure, doesn't require external IP:"
    echo -e "${GREEN}gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --tunnel-through-iap${NC}"
    echo ""
    
    echo -e "${YELLOW}Instance Details:${NC}"
    echo "Instance Name: $INSTANCE_NAME"
    echo "External IP: $EXTERNAL_IP"
    echo "Zone: $ZONE"
    echo "Username: $USERNAME"
}

# Function to set up VS Code Remote SSH
setup_vscode_remote() {
    echo -e "\n${YELLOW}VS Code Remote SSH Setup${NC}"
    echo "========================="
    echo ""
    echo "To use VS Code Remote SSH with your GCP instance:"
    echo ""
    echo "1. Install the Remote-SSH extension in VS Code"
    echo "2. Add this to your SSH config (~/.ssh/config):"
    echo ""
    
    EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
        --zone=$ZONE \
        --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
    
    echo -e "${GREEN}Host gcp-$INSTANCE_NAME
    HostName $EXTERNAL_IP
    User $USERNAME
    IdentityFile ~/.ssh/gcp_compute_engine
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null${NC}"
    echo ""
    echo "3. In VS Code, press Ctrl+Shift+P and select 'Remote-SSH: Connect to Host'"
    echo "4. Choose 'gcp-$INSTANCE_NAME' from the list"
}

# Function to troubleshoot SSH issues
troubleshoot_ssh() {
    echo -e "\n${YELLOW}SSH Troubleshooting Guide${NC}"
    echo "========================="
    echo ""
    echo "If you're having connection issues, try these commands:"
    echo ""
    echo "1. Test basic connectivity:"
    echo -e "${GREEN}gcloud compute instances describe $INSTANCE_NAME --zone=$ZONE${NC}"
    echo ""
    echo "2. Check firewall rules:"
    echo -e "${GREEN}gcloud compute firewall-rules list --filter=\"allowed[].ports=(22)\"${NC}"
    echo ""
    echo "3. View SSH keys in metadata:"
    echo -e "${GREEN}gcloud compute project-info describe --format=\"value(commonInstanceMetadata.items[ssh-keys])\"${NC}"
    echo ""
    echo "4. Debug SSH connection:"
    echo -e "${GREEN}gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --troubleshoot${NC}"
    echo ""
    echo "5. Check instance serial console output:"
    echo -e "${GREEN}gcloud compute instances get-serial-port-output $INSTANCE_NAME --zone=$ZONE${NC}"
    echo ""
    echo "6. Reset instance if needed:"
    echo -e "${GREEN}gcloud compute instances reset $INSTANCE_NAME --zone=$ZONE${NC}"
}

# Main execution
main() {
    echo -e "${GREEN}Starting GCP SSH Setup...${NC}\n"
    
    # Check prerequisites
    check_gcloud
    
    # Setup authentication
    setup_gcp_auth
    
    # Ask user what they want to do
    echo -e "\n${YELLOW}What would you like to do?${NC}"
    echo "1. Set up SSH for existing instance"
    echo "2. Create new instance and set up SSH"
    echo "3. Show connection methods for existing instance"
    echo "4. Troubleshoot SSH issues"
    echo "5. Setup VS Code Remote SSH"
    
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            setup_ssh_keys
            setup_firewall_rules
            show_connection_methods
            ;;
        2)
            create_vm_instance
            setup_ssh_keys
            setup_firewall_rules
            show_connection_methods
            ;;
        3)
            show_connection_methods
            ;;
        4)
            troubleshoot_ssh
            ;;
        5)
            setup_vscode_remote
            ;;
        *)
            echo -e "${RED}Invalid choice!${NC}"
            exit 1
            ;;
    esac
    
    echo -e "\n${GREEN}Setup complete!${NC}"
}

# Run main function
main 