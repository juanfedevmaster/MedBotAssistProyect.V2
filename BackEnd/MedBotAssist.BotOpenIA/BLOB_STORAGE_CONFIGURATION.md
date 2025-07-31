# Azure Blob Storage Configuration

This document explains how to configure Azure Blob Storage for the MedBot Assistant API.

## 📋 Environment Variables

The following environment variables control the blob storage configuration:

### Required Configuration in `.env`

```env
# Azure Blob Storage Configuration
BLOB_STORAGE_BASE_URL=https://strmedbotassist.blob.core.windows.net
BLOB_CONTAINER_NAME=instructions-files
```

### Variable Descriptions

| Variable | Description | Default Value | Example |
|----------|-------------|---------------|---------|
| `BLOB_STORAGE_BASE_URL` | Base URL of the Azure Storage Account | `https://strmedbotassist.blob.core.windows.net` | `https://youraccount.blob.core.windows.net` |
| `BLOB_CONTAINER_NAME` | Name of the blob container to access | `instructions-files` | `documents`, `files`, `attachments` |

## 🔐 JWT Configuration with SAS Token

The blob storage service requires a SAS (Shared Access Signature) token to access Azure Blob Storage. This token must be included in the JWT under the `sasToken` claim.

### JWT Payload Example

```json
{
  "iss": "MedBotAssist",
  "aud": "MedBotAssistUsers",
  "name": "username",
  "sasToken": "sp=rl&st=2024-01-01T00:00:00Z&se=2024-12-31T23:59:59Z&spr=https&sv=2023-01-03&sr=c&sig=YOUR_SAS_SIGNATURE",
  "permissions": ["UseAgent", "ViewPatients"],
  "iat": 1234567890,
  "exp": 1234567890
}
```

## 🔧 Generating SAS Tokens

### Option 1: Azure Portal (Recommended)

1. **Navigate to Azure Portal**
   - Go to your Storage Account: `strmedbotassist`
   - Click on "Containers"
   - Select the container: `instructions-files`

2. **Generate SAS Token**
   - Click "Generate SAS" button
   - **Permissions**: Select `Read` and `List`
   - **Start time**: Set to current time
   - **Expiry time**: Set according to your security policy
   - **Allowed protocols**: HTTPS only (recommended)
   - Click "Generate SAS token and URL"

3. **Copy the SAS Token**
   - Copy the generated SAS token (the part after `?`)
   - Use this token in your JWT `sasToken` claim

### Option 2: Azure CLI

```bash
# Generate SAS token for container
az storage container generate-sas \
  --account-name strmedbotassist \
  --name instructions-files \
  --permissions rl \
  --expiry 2024-12-31T23:59:59Z \
  --https-only \
  --output tsv
```

### Option 3: PowerShell

```powershell
# Generate SAS token using Azure PowerShell
$ctx = New-AzStorageContext -StorageAccountName "strmedbotassist" -UseConnectedAccount
$sasToken = New-AzStorageContainerSASToken -Name "instructions-files" -Permission "rl" -ExpiryTime (Get-Date).AddMonths(6) -Context $ctx
Write-Output $sasToken
```

## 📚 API Endpoints

The blob storage service provides the following endpoints:

### List Files
```http
GET /api/v1/blob/files
Authorization: Bearer {JWT_WITH_SAS_TOKEN}
```

### Download File
```http
GET /api/v1/blob/files/{filename}
Authorization: Bearer {JWT_WITH_SAS_TOKEN}
```

### Check File Existence
```http
GET /api/v1/blob/files/{filename}/exists
Authorization: Bearer {JWT_WITH_SAS_TOKEN}
```

### Get File Metadata
```http
HEAD /api/v1/blob/files/{filename}
Authorization: Bearer {JWT_WITH_SAS_TOKEN}
```

### Get Service Info
```http
GET /api/v1/blob/info
Authorization: Bearer {JWT_WITH_SAS_TOKEN}
```

## 🧪 Testing

### Generate Test JWT

```bash
# Generate JWT with SAS token for testing
python generate_blob_jwt.py
```

### Test with curl

```bash
# List all files
curl -X GET "http://localhost:8000/api/v1/blob/files" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Download a file
curl -X GET "http://localhost:8000/api/v1/blob/files/example.pdf" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  --output "downloaded_file.pdf"
```

### Run Service Tests

```bash
# Run blob service tests (requires valid SAS token)
python test_blob_service.py
```

## 🔒 Security Considerations

### SAS Token Security

1. **Principle of Least Privilege**
   - Only grant `Read` and `List` permissions
   - Set appropriate expiration times
   - Use HTTPS only

2. **Token Management**
   - Rotate SAS tokens regularly
   - Store tokens securely (never in source code)
   - Monitor token usage

3. **Access Control**
   - JWT authentication is required for all blob endpoints
   - Users must have appropriate permissions in JWT
   - SAS token must be valid and not expired

### Network Security

1. **HTTPS Only**
   - Always use HTTPS for blob storage access
   - Configure SAS tokens to require HTTPS

2. **IP Restrictions** (Optional)
   - Consider IP restrictions for SAS tokens in production
   - Use Azure Private Endpoints for enhanced security

## 🚨 Troubleshooting

### Common Issues

#### 403 Forbidden
- **Cause**: Invalid or expired SAS token
- **Solution**: Generate a new SAS token with proper permissions

#### 404 Not Found
- **Cause**: Container or file doesn't exist
- **Solution**: Verify container name and file paths

#### Token Expired
- **Cause**: SAS token or JWT has expired
- **Solution**: Generate new tokens with appropriate expiration

### Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| `SAS token not found in JWT` | JWT doesn't contain `sasToken` claim | Add `sasToken` to JWT payload |
| `Access denied to blob storage` | SAS token invalid/expired | Generate new SAS token |
| `Container 'instructions-files' not found` | Container doesn't exist | Create container or check name |
| `Timeout while accessing blob storage` | Network/service timeout | Check network connectivity |

## 📝 Configuration Examples

### Development Environment

```env
# .env for development
BLOB_STORAGE_BASE_URL=https://devstorageaccount.blob.core.windows.net
BLOB_CONTAINER_NAME=dev-instructions-files
```

### Production Environment

```env
# .env for production
BLOB_STORAGE_BASE_URL=https://strmedbotassist.blob.core.windows.net
BLOB_CONTAINER_NAME=instructions-files
```

### Testing Environment

```env
# .env for testing
BLOB_STORAGE_BASE_URL=https://teststorageaccount.blob.core.windows.net
BLOB_CONTAINER_NAME=test-instructions-files
```

## 🔄 Migration Guide

If you need to change storage accounts or containers:

1. **Update Environment Variables**
   ```env
   BLOB_STORAGE_BASE_URL=https://newstorageaccount.blob.core.windows.net
   BLOB_CONTAINER_NAME=new-container-name
   ```

2. **Generate New SAS Tokens**
   - Create SAS tokens for the new storage account/container
   - Update JWT generation scripts

3. **Test Configuration**
   ```bash
   python generate_blob_jwt.py
   python test_blob_service.py
   ```

4. **Deploy Changes**
   - Update production environment variables
   - Restart the application

## 📞 Support

For issues with blob storage configuration:

1. Check Azure Portal for storage account status
2. Verify SAS token permissions and expiration
3. Review application logs for detailed error messages
4. Test connectivity using Azure Storage Explorer
