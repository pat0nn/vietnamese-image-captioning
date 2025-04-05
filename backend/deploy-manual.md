# Manual Deployment of Image Uploader to Azure Container Instances

This guide provides step-by-step instructions for manually deploying the Image Uploader application to Azure Container Instances.

## Prerequisites

1. [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli) installed and authenticated
2. [Docker](https://www.docker.com/get-started) installed
3. Your model files (typically located at `/run/media/trong/New Volume/Algo/artifacts/model-checkpoint-3534:v1`)

## Step 1: Create Azure Resources

First, create the necessary Azure resources:

```bash
# Login to Azure
az login

# Create a resource group
az group create --name image-uploader-rg --location eastus

# Create a PostgreSQL server
az postgres server create \
    --resource-group image-uploader-rg \
    --name image-uploader-db \
    --location eastus \
    --admin-user dbadmin \
    --admin-password <your-secure-password> \
    --sku-name GP_Gen5_2

# Create a database
az postgres server firewall-rule create \
    --resource-group image-uploader-rg \
    --server-name image-uploader-db \
    --name AllowAllAzureIPs \
    --start-ip-address 0.0.0.0 \
    --end-ip-address 0.0.0.0

az postgres db create \
    --resource-group image-uploader-rg \
    --server-name image-uploader-db \
    --name image_caption_db

# Create storage account and file share
az storage account create \
    --name imageuploaderstorage \
    --resource-group image-uploader-rg \
    --location eastus \
    --sku Standard_LRS

# Get storage key
STORAGE_KEY=$(az storage account keys list \
    --resource-group image-uploader-rg \
    --account-name imageuploaderstorage \
    --query "[0].value" -o tsv)

# Create file share
az storage share create \
    --name image-uploader-share \
    --account-name imageuploaderstorage \
    --account-key $STORAGE_KEY
```

## Step 2: Upload Model Files to Azure File Share

Use Azure Storage Explorer or the Azure CLI to upload your model files:

1. Install Azure Storage Explorer
2. Connect to your storage account using the storage key
3. Create a 'model' folder in the file share
4. Upload your model files to this folder
5. Create an 'uploads' folder for saving uploaded images

### Option 1: Using Azure CLI

```bash
# Create model and uploads directories in the file share
az storage directory create \
    --name model \
    --share-name image-uploader-share \
    --account-name imageuploaderstorage \
    --account-key $STORAGE_KEY

az storage directory create \
    --name uploads \
    --share-name image-uploader-share \
    --account-name imageuploaderstorage \
    --account-key $STORAGE_KEY

# Upload model files (example)
az storage file upload-batch \
    --source /path/to/model/files \
    --destination image-uploader-share/model \
    --account-name imageuploaderstorage \
    --account-key $STORAGE_KEY
```

### Option 2: Using AzCopy (Recommended for large model files)

AzCopy is recommended for transferring large model files due to its better performance:

1. Install AzCopy from https://docs.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10
2. Generate a SAS token for your file share in Azure Portal or using CLI
3. Use AzCopy to transfer files:

```bash
# Example AzCopy command
azcopy copy "/path/to/model/files" \
"https://imageuploaderstorage.file.core.windows.net/image-uploader-share/model?[SAS_TOKEN]" \
--recursive=true
```

For example:
```bash
# Example with actual path - replace the SAS token with your own
azcopy copy "/run/media/trong/New Volume/Algo/artifacts/model-checkpoint-3534:v1" \
"https://imageuploaderstorage.file.core.windows.net/image-uploader-share/model?se=2025-12-31T23%3A59%3A00Z&sp=rwl&sv=2024-08-04&sr=s&sig=XXXXX" \
--recursive=true
```

To generate a SAS token via CLI:
```bash
end=$(date -u -d "30 days" '+%Y-%m-%dT%H:%MZ')
sas=$(az storage share generate-sas \
    --name image-uploader-share \
    --account-name imageuploaderstorage \
    --account-key $STORAGE_KEY \
    --permissions rwdl \
    --expiry $end \
    --output tsv)
echo "https://imageuploaderstorage.file.core.windows.net/image-uploader-share?$sas"
```

## Step 3: Build and Push Docker Image

```bash
# Create an Azure Container Registry
az acr create \
    --resource-group image-uploader-rg \
    --name imageuploaderregistry \
    --sku Basic

# Login to ACR
az acr login --name imageuploaderregistry

# Build and push the Docker image
az acr build --registry imageuploaderregistry --image image-uploader:latest .
```

## Step 4: Deploy to Azure Container Instances

Create an environment variable file for the YAML template:

```bash
cat > .env << EOF
REGISTRY=imageuploaderregistry.azurecr.io
DB_HOST=image-uploader-db.postgres.database.azure.com
DB_PORT=5432
DB_NAME=image_caption_db
DB_USER=dbadmin@image-uploader-db
DB_PASSWORD=<your-secure-password>
STORAGE_ACCOUNT_NAME=imageuploaderstorage
STORAGE_ACCOUNT_KEY=$STORAGE_KEY
FILE_SHARE_NAME=image-uploader-share
EOF
```

Now deploy the container instance using the YAML template:

```bash
# Create a service principal for ACR access
ACR_REGISTRY_ID=$(az acr show --name imageuploaderregistry --query id --output tsv)

# Create service principal with acrpull role
SP_NAME="imageuploaderregistry-pull"
SP_PASSWORD=$(az ad sp create-for-rbac --name "http://$SP_NAME" --scopes $ACR_REGISTRY_ID --role acrpull --query password --output tsv)

# Get the service principal's app ID using display name 
SP_APP_ID=$(az ad sp list --display-name "$SP_NAME" --query "[0].appId" --output tsv)

# If SP_APP_ID is empty, try an alternative approach
if [ -z "$SP_APP_ID" ]; then
    echo "Trying alternative method to get service principal ID..."
    SP_APP_ID=$(az ad sp list --query "[?displayName=='$SP_NAME'].appId" --output tsv)
fi

echo "Service Principal App ID: $SP_APP_ID"

# Use environment variables from .env file
source .env

# Replace placeholders in the YAML file
envsubst < azure-container-instance.yaml > azure-container-instance-resolved.yaml

# Deploy the container instance
az container create \
    --resource-group image-uploader-rg \
    --file azure-container-instance-resolved.yaml \
    --registry-login-server imageuploaderregistry.azurecr.io \
    --registry-username $SP_APP_ID \
    --registry-password $SP_PASSWORD
```

## Step 5: Access the Application

Once deployed, you can access the application using the FQDN:

```bash
FQDN=$(az container show \
    --resource-group image-uploader-rg \
    --name image-uploader-api \
    --query ipAddress.fqdn \
    --output tsv)

echo "Application URL: http://$FQDN:5000"
```

## Updating the Application

To update the application:

1. Make your changes to the code
2. Build and push a new Docker image:
   ```bash
   az acr build --registry imageuploaderregistry --image image-uploader:latest .
   ```
3. Restart the container instance:
   ```bash
   az container restart --name image-uploader-api --resource-group image-uploader-rg
   ```

## Monitoring and Troubleshooting

- **View container logs**:
  ```bash
  az container logs --name image-uploader-api --resource-group image-uploader-rg
  ```

- **Connect to the container**:
  ```bash
  az container exec --name image-uploader-api --resource-group image-uploader-rg --exec-command /bin/bash
  ```

- **Check container state**:
  ```bash
  az container show --name image-uploader-api --resource-group image-uploader-rg
  ```

## Clean Up

To remove all resources when they're no longer needed:

```bash
az group delete --name image-uploader-rg --yes
``` 



azcopy copy "/run/media/trong/New Volume/Algo/ViT-BARTpho_3-23" \
"https://imageuploaderstorage1.file.core.windows.net/image-uploader-share/model?se=2025-12-31T23%3A59%3A00Z&sp=rwl&sv=2024-08-04&sr=s&sig=7Aqz9C7Uu0v3c4NtMnTYYsl1tQSM7Q5OxTu/8feTyd0%3D" \
--recursive=true
