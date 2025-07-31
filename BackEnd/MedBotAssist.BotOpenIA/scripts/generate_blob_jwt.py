#!/usr/bin/env python3
"""
Generador de JWT específico para pruebas de Blob Storage
"""

import jwt
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_blob_test_jwt():
    """Generate a test JWT with SAS token for blob storage testing."""
    
    # JWT Configuration from environment variables
    SECRET = os.getenv("JWT_SECRET", "a1B2c3D4e5F6g7H8i9J0kLmNoPqRsTuVwXyZ1234567890==!")
    ISSUER = os.getenv("JWT_ISSUER", "MedBotAssist")
    AUDIENCE = os.getenv("JWT_AUDIENCE", "MedBotAssistUsers")
    EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    
    # Blob Storage Configuration from environment variables
    BLOB_BASE_URL = os.getenv("BLOB_STORAGE_BASE_URL", "https://strmedbotassist.blob.core.windows.net")
    BLOB_CONTAINER = os.getenv("BLOB_CONTAINER_NAME", "instructions-files")
    
    # Example SAS token (you should replace this with a real one)
    # This is a sample format - replace with actual SAS token from Azure
    SAMPLE_SAS_TOKEN = "sp=rl&st=2024-01-01T00:00:00Z&se=2024-12-31T23:59:59Z&spr=https&sv=2023-01-03&sr=c&sig=REPLACE_WITH_REAL_SAS_SIGNATURE"
    
    # Payload the token
    now = datetime.utcnow()
    payload = {
        "iss": ISSUER,                              # Issuer
        "aud": AUDIENCE,                            # Audience  
        "sub": "user_12345",                        # Subject (user ID)
        "name": "testuser",                         # Username
        "email": "testuser@medbot.com",
        "role": "doctor",
        "sasToken": SAMPLE_SAS_TOKEN,               # ← SAS token for blob storage
        "permissions": ["UseAgent", "ViewPatients"], # User permissions
        "iat": now,                                 # Issued at
        "exp": now + timedelta(minutes=EXPIRATION_MINUTES)  # Expiration
    }
    
    # Generate token
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    
    return token, payload

def main():
    print("🗂️  Blob Storage JWT Generator for MedBot Assistant")
    print("=" * 70)
    
    try:
        token, payload = generate_blob_test_jwt()

        print("✅ JWT with SAS token generated successfully!")
        print(f"\n📋 Token payload:")
        print(json.dumps(payload, indent=2, default=str))
        
        print(f"\n🎫 JWT Token:")
        print(f"Bearer {token}")
        
        print(f"\n📝 For use in Postman/Curl:")
        print(f"Authorization: Bearer {token}")

        print(f"\n🧪 Test curl commands:")
        print(f"\n# 1. List all files in instructions-files container:")
        print(f'curl -X GET "http://localhost:8000/api/v1/blob/files" \\')
        print(f'  -H "Authorization: Bearer {token}"')
        
        print(f"\n# 2. Get blob service info:")
        print(f'curl -X GET "http://localhost:8000/api/v1/blob/info" \\')
        print(f'  -H "Authorization: Bearer {token}"')
        
        print(f"\n# 3. Check if a file exists:")
        print(f'curl -X GET "http://localhost:8000/api/v1/blob/files/example.pdf/exists" \\')
        print(f'  -H "Authorization: Bearer {token}"')
        
        print(f"\n# 4. Download a specific file:")
        print(f'curl -X GET "http://localhost:8000/api/v1/blob/files/example.pdf" \\')
        print(f'  -H "Authorization: Bearer {token}" \\')
        print(f'  --output "downloaded_file.pdf"')
        
        print(f"\n# 5. Get file metadata (HEAD request):")
        print(f'curl -X HEAD "http://localhost:8000/api/v1/blob/files/example.pdf" \\')
        print(f'  -H "Authorization: Bearer {token}"')

        print(f"\n⚠️  IMPORTANT NOTES:")
        print(f"📌 Replace the SAS token in the payload with a real one from Azure Portal")
        print(f"📌 SAS token must have 'Read' and 'List' permissions for the container")
        print(f"📌 Container name: {os.getenv('BLOB_CONTAINER_NAME', 'instructions-files')}")
        print(f"📌 Storage URL: {os.getenv('BLOB_STORAGE_BASE_URL', 'https://strmedbotassist.blob.core.windows.net')}")
        print(f"⏰ Token valid for: {os.getenv('JWT_EXPIRATION_MINUTES', '60')} minutes")

        print(f"\n🔐 To get a real SAS token:")
        print(f"1. Go to Azure Portal → Storage Account → strmedbotassist")
        print(f"2. Navigate to Containers → {os.getenv('BLOB_CONTAINER_NAME', 'instructions-files')}")
        print(f"3. Click 'Generate SAS' with Read/List permissions")
        print(f"4. Copy the SAS token and replace it in this script")

    except Exception as e:
        print(f"❌ Error generating JWT: {e}")

if __name__ == "__main__":
    main()
