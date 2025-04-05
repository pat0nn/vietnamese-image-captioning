#!/bin/bash

# Exit on error
set -e

# Configuration
RESOURCE_GROUP="image-uploader-rg"
LOCATION="eastus"
ACR_NAME="imageuploaderregistry"
CONTAINER_NAME="image-uploader-api"
POSTGRES_SERVER_NAME="image-uploader-db"
POSTGRES_DB="image_caption_db"
POSTGRES_USER="dbadmin"
POSTGRES_PASSWORD="$(openssl rand -base64 16)"
STORAGE_ACCOUNT_NAME="imageuploaderstorage1"
FILE_SHARE_NAME="image-uploader-share"

# Create resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Azure Container Registry
echo "Creating Azure Container Registry..."
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic

# Log in to ACR
echo "Logging in to ACR..."
az acr login --name $ACR_NAME

# Build and push Docker image
echo "Building and pushing Docker image..."
az acr build --registry $ACR_NAME --image image-uploader:latest .

# Create Azure Database for PostgreSQL
echo "Creating Azure Database for PostgreSQL..."
az postgres server create \
    --resource-group $RESOURCE_GROUP \
    --name $POSTGRES_SERVER_NAME \
    --location $LOCATION \
    --admin-user $POSTGRES_USER \
    --admin-password $POSTGRES_PASSWORD \
    --sku-name GP_Gen5_2

# Configure firewall rules for PostgreSQL
echo "Configuring PostgreSQL firewall..."
az postgres server firewall-rule create \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_SERVER_NAME \
    --name AllowAllAzureIPs \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

# Create database
echo "Creating database..."
az postgres db create \
    --resource-group $RESOURCE_GROUP \
    --server-name $POSTGRES_SERVER_NAME \
    --name $POSTGRES_DB

# Create storage account for model and uploads
echo "Creating storage account..."
az storage account create \
    --name $STORAGE_ACCOUNT_NAME \
    --resource-group $RESOURCE_GROUP \
    --location $LOCATION \
    --sku Standard_LRS

# Get storage account key
STORAGE_ACCOUNT_KEY=$(az storage account keys list \
    --resource-group $RESOURCE_GROUP \
    --account-name $STORAGE_ACCOUNT_NAME \
    --query "[0].value" -o tsv)

# Create file share for model and uploads
echo "Creating file share..."
az storage share create \
    --name $FILE_SHARE_NAME \
    --account-name $STORAGE_ACCOUNT_NAME \
    --account-key $STORAGE_ACCOUNT_KEY

# Print instructions for uploading model to file share
echo "Please upload your model files to Azure File Share using Azure Storage Explorer:"
echo "1. Connect to your storage account: $STORAGE_ACCOUNT_NAME"
echo "2. Navigate to File Shares -> $FILE_SHARE_NAME"
echo "3. Create a folder called 'model' and upload your model files there"
echo "4. Create a folder called 'uploads' for saving uploaded images"
echo ""
echo "Press Enter when you have completed this step..."
read -p ""

# Create ACR service principal for container instance to pull from ACR
echo "Creating ACR service principal..."
ACR_REGISTRY_ID=$(az acr show --name $ACR_NAME --query id --output tsv)

# Create service principal and get password
SP_NAME="http://$ACR_NAME-pull"
SP_PASSWORD=$(az ad sp create-for-rbac --name $SP_NAME --scopes $ACR_REGISTRY_ID --role acrpull --query password --output tsv)

# Get the service principal's app ID using display name instead of ID
# This is more reliable when the SP may already exist
SP_APP_ID=$(az ad sp list --display-name "$ACR_NAME-pull" --query "[0].appId" --output tsv)

# If the SP_APP_ID is empty, try an alternative approach
if [ -z "$SP_APP_ID" ]; then
    echo "Trying alternative method to get service principal ID..."
    SP_APP_ID=$(az ad sp list --query "[?displayName=='$ACR_NAME-pull'].appId" --output tsv)
fi

# Verify we have the necessary credentials
if [ -z "$SP_APP_ID" ] || [ -z "$SP_PASSWORD" ]; then
    echo "Error: Could not retrieve service principal credentials."
    echo "Please create a service principal manually with the acrpull role on $ACR_NAME"
    exit 1
fi

echo "Service principal created/updated successfully."

# Deploy container instance
echo "Deploying container instance..."
az container create \
    --resource-group $RESOURCE_GROUP \
    --name $CONTAINER_NAME \
    --image ${ACR_NAME}.azurecr.io/image-uploader:latest \
    --registry-login-server ${ACR_NAME}.azurecr.io \
    --registry-username $SP_APP_ID \
    --registry-password $SP_PASSWORD \
    --dns-name-label $CONTAINER_NAME \
    --ports 5000 \
    --cpu 2 \
    --memory 4 \
    --environment-variables \
        DB_HOST="${POSTGRES_SERVER_NAME}.postgres.database.azure.com" \
        DB_PORT="5432" \
        DB_NAME="$POSTGRES_DB" \
        DB_USER="${POSTGRES_USER}@${POSTGRES_SERVER_NAME}" \
        DB_PASSWORD="$POSTGRES_PASSWORD" \
        MODEL_PATH="/mnt/azurefile/model" \
        UPLOAD_FOLDER="/mnt/azurefile/uploads" \
    --azure-file-volume-account-name $STORAGE_ACCOUNT_NAME \
    --azure-file-volume-account-key $STORAGE_ACCOUNT_KEY \
    --azure-file-volume-share-name $FILE_SHARE_NAME \
    --azure-file-volume-mount-path "/mnt/azurefile"

# Output connection information
CONTAINER_FQDN=$(az container show --resource-group $RESOURCE_GROUP --name $CONTAINER_NAME --query ipAddress.fqdn --output tsv)

echo "========================================================"
echo "Deployment completed successfully!"
echo "API URL: http://$CONTAINER_FQDN:5000"
echo "PostgreSQL server: ${POSTGRES_SERVER_NAME}.postgres.database.azure.com"
echo "PostgreSQL username: ${POSTGRES_USER}@${POSTGRES_SERVER_NAME}"
echo "PostgreSQL password: $POSTGRES_PASSWORD"
echo "PostgreSQL database: $POSTGRES_DB"
echo "========================================================" 