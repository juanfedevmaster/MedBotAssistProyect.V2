# MedBot Assistant API

API for medical assistant with AI agents and direct SQL queries.

## Project Structure

```
MedBotAssist.BotOpenIA/
├── app/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── medical_query_agent.py    # Main medical agent
│   │   └── tools.py                  # Agent tools
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── agent.py             # Agent endpoints
│   │   └── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py                # Application configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py              # Database models
│   │   └── schemas.py               # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database_service.py      # SQL database service
│   │   ├── jwt_service.py           # JWT authentication service
│   │   └── permission_context.py    # Permission context
│   └── __init__.py
├── main.py                          # Main FastAPI application
├── server.py                        # Deployment script
├── startup.sh                       # Startup script for Azure
├── runtime.txt                      # Python version for Azure
├── requirements.txt                 # Dependencies
├── .env.example                     # Environment variables example
└── README.md                        # This file
```

## Configuration

1. **Copy the environment variables file:**
   ```bash
   copy .env.example .env
   ```

2. **Configure your OpenAI API key in the `.env` file:**
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

3. **Configure SQL Server database credentials (optional):**
   ```
   DB_SERVER=your_server.database.windows.net
   DB_DATABASE=your_database
   DB_USER=your_username
   DB_PASSWORD=your_password
   ```

4. **Configure external backend for patient management:**
   ```
   EXTERNAL_BACKEND_API_URL=http://localhost:5098/api/
   ```

5. **Configure JWT credentials:**
   ```
   JWT_SECRET=your_jwt_secret
   JWT_ISSUER=MedBotAssist
   JWT_AUDIENCE=MedBotAssistUsers
   JWT_EXPIRATION_MINUTES=60
   ```

6. **Configure Azure Blob Storage:**
   ```
   BLOB_STORAGE_BASE_URL=https://strmedbotassist.blob.core.windows.net
   BLOB_CONTAINER_NAME=instructions-files
   ```

## Installation

```bash
pip install -r requirements.txt
```

## Execution

### Option 1: Using the main script
```bash
python main.py
```

### Option 2: Using uvicorn directly

#### For Windows (Recommended - Avoids multiprocessing issues):
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### For Linux/Mac (with auto-reload):
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Alternative with reload for Windows (if needed):
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Option 3: Using the Windows development server (Recommended for development)
```bash
python dev_server.py
```

### Option 4: For deployment (Azure)
```bash
python server.py
```

## Troubleshooting

### Windows Multiprocessing Error with uvicorn --reload

If you encounter multiprocessing errors on Windows when using `--reload`, try these solutions:

1. **Use without reload (fastest solution):**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

2. **Use the development server:**
   ```bash
   python dev_server.py
   ```

3. **Use localhost instead of 0.0.0.0:**
   ```bash
   uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

4. **Use the main script:**
   ```bash
   python main.py
   ```

## Available Endpoints

### 📊 Automatic Documentation
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### 🤖 Medical Agent Endpoints

#### Chat with the Agent
- **POST** `/api/v1/agent/chat` - Chat with the medical agent
- **GET** `/api/v1/agent/tools` - List available agent tools
- **POST** `/api/v1/agent/health` - Medical agent status

#### Conversation Management
- **GET** `/api/v1/agent/conversation/{id}` - Get conversation history
- **DELETE** `/api/v1/agent/conversation/{id}` - Clear conversation history

### 🗂️ Blob Storage Endpoints

#### File Management
- **GET** `/api/v1/blob/files` - List all files in instructions-files container
- **GET** `/api/v1/blob/files/{filename}` - Download specific file
- **HEAD** `/api/v1/blob/files/{filename}` - Get file metadata
- **GET** `/api/v1/blob/files/{filename}/exists` - Check if file exists
- **GET** `/api/v1/blob/info` - Get blob service information

## Agent Tools

The medical agent has access to the following tools:

### 🔍 Patient Search
- **search_patients** - General search by natural query
- **search_patients_by_name** - Name search with normalization
- **filter_patients_by_demographics** - Filters by age, email, birth year
- **get_patient_by_id** - Complete details only with IdentificationNumber

### 📊 Statistics
- **get_patients_summary** - Statistical summary (counts only, no details)

### 🩺 Medical History
- **get_patient_medical_history** - Complete medical history with appointments, notes and diagnoses
- **get_patient_diagnoses_summary** - Summary focused on diagnoses and treatments
- **count_patients_by_diagnosis** - Statistical count of patients by specific diagnosis

### 🔍 Diagnosis Search
- **search_patients_by_diagnosis** - Complete search of patients with a specific diagnosis
- **get_patient_names_by_diagnosis** - Gets names and IDs of patients with specific diagnosis

### 📞 Contact Search
- **search_patients_by_condition** - Search by contact information

### ➕ Patient Management
- **create_patient** - Create new patients in the external system
  - **Requires permission:** ManagePatients
  - **External backend:** Consumes API at `EXTERNAL_BACKEND_API_URL`
  - **Endpoint:** POST `/api/Patient/create`
  - **Authentication:** Current user's JWT token
- **update_patient** - Update existing patient information
  - **Requires permission:** ManagePatients
  - **External backend:** Consumes API at `EXTERNAL_BACKEND_API_URL`
  - **Endpoint:** PUT `/api/Patient/update-patient`
  - **Authentication:** Current user's JWT token

## Usage Examples

### Chat with the agent:
```json
POST /api/v1/agent/chat
{
  "message": "Search for patients with the last name García",
  "conversation_id": "conv_123"
}
```

### Create a new patient:
```json
POST /api/v1/agent/chat
{
  "message": "Create a new patient with name 'Juanfe Test', identification '123456789', birth date '2020-07-27T22:25:33.321Z', age 25, phone '3004441111' and email 'juanfe.test2@gmail.com'",
  "conversation_id": "conv_456"
}
```

### Update an existing patient:
```json
POST /api/v1/agent/chat
{
  "message": "Update the patient with identification '123456789', change their email to 'nuevo.email@gmail.com' and phone to '+57-301-555-1234'",
  "conversation_id": "conv_789"
}
```

### Query complete medical history:
```json
POST /api/v1/agent/chat
{
  "message": "Show the complete medical history of the patient with identification '123456789'",
  "conversation_id": "conv_101"
}
```

### Query diagnoses and treatments:
```json
POST /api/v1/agent/chat
{
  "message": "What are the diagnoses of the patient with identification '987654321'?",
  "conversation_id": "conv_102"
}
```

### Count patients by diagnosis:
```json
POST /api/v1/agent/chat
{
  "message": "How many patients have diabetes?",
  "conversation_id": "conv_103"
}
```

### Diagnosis statistics:
```json
POST /api/v1/agent/chat
{
  "message": "Show the count of patients with hypertension",
  "conversation_id": "conv_104"
}
```

### Search patients by diagnosis (complete information):
```json
POST /api/v1/agent/chat
{
  "message": "Search all patients who have diabetes",
  "conversation_id": "conv_105"
}
```

### Get patient names by diagnosis:
```json
POST /api/v1/agent/chat
{
  "message": "What is the name of the patient who suffers from Hypertension?",
  "conversation_id": "conv_106"
}
```

### Direct diagnosis query:
```json
POST /api/v1/agent/chat
{
  "message": "Who has asthma?",
  "conversation_id": "conv_107"
}
```

### Expected response:
```json
{
  "response": "I found 3 patients with the last name García:\n\n1. Patient María García with identification ID002, 32 years old, born on August 20, 1992, phone 555-5678, email maria.garcia@email.com\n\n2. Patient José García López with identification ID015, 28 years old...",
  "conversation_id": "conv_123",
  "agent_used_tools": true,
  "available_tools": ["search_patients", "search_patients_by_name", "get_patients_summary", "filter_patients_by_demographics", "search_patients_by_condition", "get_patient_by_id", "get_patient_medical_history", "get_patient_diagnoses_summary", "count_patients_by_diagnosis", "search_patients_by_diagnosis", "get_patient_names_by_diagnosis", "create_patient", "update_patient"],
  "status": "success"
}
```

### Get available tools:
```bash
GET /api/v1/agent/tools
```

## Main Features

✅ **Direct SQL Server query** - No intermediaries, real-time data  
✅ **Conversational agent** - Natural language processing with OpenAI  
✅ **Normalized search** - Finds "García" by searching "garcia"  
✅ **Multiple tools** - Search, filtering, statistics, creation and update  
✅ **External backend integration** - Patient creation and update via HTTP API  
✅ **Conversation history** - Maintains context between queries  
✅ **Complete REST API** - Documented and validated endpoints  
✅ **Azure compatible** - Configured for App Service  

## Security System:

- 🔐 Mandatory JWT authentication in /api/v1/agent/chat
- 🛡️ ViewPatients permission validation for query tools
- 🛡️ ManagePatients permission validation for patient creation and update
- 🚫 Custom error messages for access denied
- 🔗 External backend integration for write operations

## Search Features

### 🔤 Text Normalization
The system automatically normalizes searches for greater flexibility:

- **"sanchez"** → Finds **"Sánchez García"**
- **"jose maria"** → Finds **"José María"**
- **"PEREZ"** → Finds **"Pérez López"**

### 🎯 Search Types
- **By full or partial name**
- **By demographic information** (age, email)
- **By contact information** (phone, email)
- **General searches** with natural language

## Patient Management

### ➕ Patient Creation
The `create_patient` tool allows creating new patients through the conversational agent:

**Requirements:**
- Authenticated user with JWT token
- `ManagePatients` permission in the token
- External backend running at `EXTERNAL_BACKEND_API_URL`

**Request format:**
```
"Create a new patient with name '[NAME]', identification '[ID]', birth date '[DATE]', age [AGE], phone '[PHONE]' and email '[EMAIL]'"
```

**Example:**
```
"Create a new patient with name 'Juan Pérez', identification '12345678', birth date '1990-05-15T00:00:00.000Z', age 33, phone '+57-300-123-4567' and email 'juan.perez@email.com'"
```

**Internal process:**
1. ManagePatients permission validation
2. JWT token extraction from context
3. JSON payload construction
4. HTTP POST call to external backend
5. Response handling (success/error)

**Expected responses:**
- ✅ **200/201:** Patient created successfully
- ❌ **400:** Data validation error
- ❌ **401:** Invalid or expired JWT token
- ❌ **403:** No ManagePatients permissions
- ❌ **500:** External server error

### 🔄 Patient Update
The `update_patient` tool allows updating existing patient information through the conversational agent:

**Requirements:**
- Authenticated user with JWT token
- `ManagePatients` permission in the token
- External backend running at `EXTERNAL_BACKEND_API_URL`
- Patient identification number (mandatory)

**Request format:**
```
"Update the patient with identification '[ID]', change [FIELD1] to '[VALUE1]', [FIELD2] to '[VALUE2]'"
```

**Examples:**
```
"Update the patient with identification '12345678', change their email to 'nuevo@email.com'"
"Update the patient with identification '87654321', change their name to 'María Elena García' and phone to '+57-301-555-9999'"
"Update the patient with identification '11223344', change their age to 35 and birth date to '1988-12-25T00:00:00.000Z'"
```

**Internal process:**
1. ManagePatients permission validation
2. JWT token extraction from context
3. Search for current patient with `get_patient_by_id`
4. Combine existing data with new values
5. HTTP PUT call to external backend
6. Response handling (success/error)

**Expected responses:**
- ✅ **200/204:** Patient updated successfully
- ❌ **400:** Data validation error
- ❌ **401:** Invalid or expired JWT token
- ❌ **403:** No ManagePatients permissions
- ❌ **404:** Patient not found
- ❌ **500:** External server error

## Architecture

### 🗄️ Data
- **SQL Server** as single source of truth
- **Direct queries** without cache or synchronization
- **Real-time normalization** for searches

### 🤖 AI Agent
- **LangChain** for agent management
- **OpenAI GPT** for language processing
- **Specialized tools** for data access

### 🔐 Security (JWT Ready)
- **JWT configured** for future authentication
- **Environment variables** for secrets
- **Ready configuration** for tool-based authorization

## Technologies

- **FastAPI** - Modern web framework
- **Pydantic** - Data validation
- **OpenAI** - GPT for conversation
- **LangChain** - Framework for AI agents
- **SQLAlchemy** - ORM for SQL Server
- **pyodbc** - Database driver
- **httpx** - HTTP client for external backend integration
- **PyJWT** - JWT token processing

## Azure Deployment

The project is configured for Azure App Service:

1. **startup.sh** - Initialization script
2. **server.py** - Production server  
3. **runtime.txt** - Specifies Python 3.11.12
4. **requirements.txt** - All dependencies

## Error Correction:

In critical files, app services must use Unix format (\n). 
If it fails, you should run these scripts:

# Convert startup.sh
(Get-Content startup.sh -Raw) -replace "`r`n", "`n" | Set-Content startup.sh -NoNewline

# Convert requirements.txt  
(Get-Content requirements.txt -Raw) -replace "`r`n", "`n" | Set-Content requirements.txt -NoNewline

# Convert server.py
(Get-Content server.py -Raw) -replace "`r`n", "`n" | Set-Content server.py -NoNewline

# Convert runtime.txt
(Get-Content runtime.txt -Raw) -replace "`r`n", "`n" | Set-Content runtime.txt -NoNewline

# ✅ SIMPLIFIED VECTORIZATION SYSTEM - COMPLETED

## 📋 Summary of Implemented Changes

### 🚀 **Simplified Architecture**
- **Previous approach**: Individual file vectorization with change tracking
- **New approach**: Complete re-vectorization every time a file is uploaded
- **Benefit**: Less complexity, always consistent, less code to maintain

### 🔧 **Simplified Endpoints**
**✅ Maintained Endpoints:**
- `/revectorize-all` - Re-vectorizes all files from blob storage
- `/clear-vectors` - Utility to clear vectors
- `/search-instructives` - Search in vectorized instructional documents
- `/available-instructives` - List of available instructional documents
- `/search-by-filename` - Search in specific file

**❌ Removed Endpoints:**
- `/vectorize-file` - No longer needed with simplified approach
- `/vectorization-stats` - Non-essential functionality removed

### 📦 **Updated Dependencies**
- ChromaDB updated to version 1.0.15 (compatible with precompiled binaries)
- All vectorization dependencies installed correctly
- Testing system with pytest configured

### ✅ **Preserved Functionalities**
- ✅ Instructional search tools fully functional
- ✅ Integration with medical agent intact
- ✅ Logging and cleanup system operational
- ✅ File name tracking maintained
- ✅ Authentication and permissions working

### 🧪 **Testing System**
- Automated testing script (`test_simplified_vectorization.py`)
- Verification of available and deprecated endpoints
- Basic functionality tests
- All tests pass successfully: **5/5** ✅

## 🎯 **Final Result**

The system implements a solid architecture, due to the importance of medical instructional documents:
> **"Every time a file is uploaded, re-vectorize everything"**

### Advantages of the new system:
1. **Simplicity**: Less code, less complexity
2. **Consistency**: Always all files processed with the same version
3. **Maintainability**: Fewer methods, fewer endpoints, fewer potential bugs
4. **Robustness**: Avoids synchronization problems between files

### Current status:
- ✅ Server running correctly
- ✅ All essential endpoints operational
- ✅ Simplified vectorization system implemented
- ✅ Dependencies correctly installed
- ✅ Automated tests passing

## 📝 **Execution Steps**

1. **To use the system**:
   ```bash
   # Start server
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   
   # Re-vectorize all files
   GET /api/v1/vectorization/revectorize-all?sas_token=<TOKEN>
   
   # Search in instructional documents
   GET /api/v1/vectorization/search-instructives?query=<QUERY>
   ```

2. **For testing**:
   ```bash
   python test_simplified_vectorization.py
   ```

3. **For future development**:
   - Integrate with file upload system
   - Configure webhooks to trigger automatic re-vectorization
   - Optimize performance for large file volumes

# Auto-Vectorization on Server Startup

## Description

This functionality allows that when the FastAPI server restarts and the in-memory vector database (`VectorInMemory`) is empty, it automatically processes and vectorizes all files found in the configured Azure Blob Storage container.

## Required Configuration

### 1. Environment Variables (.env)

```properties
# Azure Blob Storage Configuration
BLOB_STORAGE_BASE_URL=https://strmedbotassist.blob.core.windows.net
BLOB_CONTAINER_NAME=instructions-files
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=strmedbotassist;AccountKey=YOUR_ACCOUNT_KEY_HERE;EndpointSuffix=core.windows.net
AUTO_VECTORIZE_ON_STARTUP=true
```

### 2. Azure Storage Connection String

You need to obtain the connection string from your Azure Storage account:

1. Go to the Azure Portal
2. Navigate to your Storage Account (`strmedbotassist`)
3. In the left menu, select "Access keys"
4. Copy the "Connection string" from key1 or key2
5. Replace `YOUR_ACCOUNT_KEY_HERE` in the `.env` file

## How It Works

### When It Executes

Auto-vectorization runs automatically when:

1. **The server starts** (`python -m uvicorn main:app --host 0.0.0.0 --port 8000`)
2. **The vector database is empty** (0 documents)
3. **AUTO_VECTORIZE_ON_STARTUP=true** in the configuration

### What It Does

1. **Verifies configuration**: Checks that all variables are configured
2. **Lists files**: Gets all files from the Azure Blob container
3. **Processes each file**: Downloads, extracts text and vectorizes each file
4. **Stores in memory**: Saves vectors in the `VectorInMemory` database
5. **Logs results**: Detailed logs of the process

### Supported File Types

- **PDF** (.pdf)
- **Word** (.docx)
- **HTML** (.html, .htm)
- **Plain text** (.txt)

## Benefits for Deployments

### Problem Solved

```bash
# BEFORE: With each deploy you lost all vectors
Deploy #1: 100 vectorized documents ✅
Deploy #2: 0 documents ❌ (lost)
Deploy #3: 0 documents ❌ (lost)

# NOW: Auto-recovery after each deploy
Deploy #1: 100 vectorized documents ✅
Deploy #2: 100 auto-vectorized documents ✅ (automatically recovered)
Deploy #3: 100 auto-vectorized documents ✅ (automatically recovered)
```

### CI/CD Pipeline

```yaml
# azure-pipelines.yml
steps:
- task: AzureWebApp@1
  inputs:
    azureSubscription: 'service-connection'
    appName: 'medbot-api'
    package: '.'
    
# When deploying:
# 1. New instance starts
# 2. Vector DB is empty
# 3. Auto-vectorization executes
# 4. All documents are processed automatically
# 5. API ready to use
```

## Example Logs

### Successful Startup
```
INFO: FastAPI application starting up...
INFO: Vector database is empty. Starting auto-vectorization from Azure Blob Storage...
INFO: Found 15 files in Azure Blob Storage. Starting auto-vectorization...
INFO: Auto-vectorizing file 1/15: 'medical_protocols.pdf'
INFO: Auto-vectorizing file 2/15: 'drug_interactions.docx'
...
INFO: ✅ Auto-vectorization completed: 15 files processed, 847 chunks created
INFO: FastAPI application startup completed
```

### Startup with Non-Empty Vector DB
```
INFO: FastAPI application starting up...
INFO: ⏭️ Auto-vectorization skipped: Vector database already contains 847 documents
INFO: FastAPI application startup completed
```

### Startup with Auto-vectorization Disabled
```
INFO: FastAPI application starting up...
INFO: 🔒 Auto-vectorization is disabled in configuration
INFO: FastAPI application startup completed
```

## Configuration for Different Environments

### Development (with --reload)
```bash
# Vectors restart with each code change
# but auto-vectorize each time
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Production (without --reload)
```bash
# Vectors persist until next deploy
# Only auto-vectorize on startup if empty
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

## Troubleshooting

### Error: Azure Storage SDK not available
```bash
pip install azure-storage-blob azure-identity
```

### Error: Connection string not configured
```
ERROR: Azure Storage connection string not configured
```
**Solution**: Configure `AZURE_STORAGE_CONNECTION_STRING` in `.env`

### Error: Access denied to Azure Storage
```
ERROR: Error listing blobs: (403) Forbidden
```
**Solution**: Verify that the connection string is correct and has read permissions

### Auto-vectorization doesn't execute
**Check**:
1. `AUTO_VECTORIZE_ON_STARTUP=true`
2. Vector DB is actually empty (no previous documents)
3. Connection string is valid
4. Container exists and has files

## Performance

### Startup Time
- **No files**: ~2-3 seconds
- **With 10 files**: ~30-45 seconds
- **With 50 files**: ~2-3 minutes

### Memory Usage
- Each vectorized document consumes ~1-2 MB in RAM
- 100 documents ≈ 100-200 MB additional

### Optimizations
- Only executes when DB is empty
- Asynchronous file processing
- Detailed logs for monitoring
- Error handling without failing startup

## Disable Auto-Vectorization

To disable this functionality:

```properties
# In .env
AUTO_VECTORIZE_ON_STARTUP=false
```

Or simply don't configure `AZURE_STORAGE_CONNECTION_STRING`.