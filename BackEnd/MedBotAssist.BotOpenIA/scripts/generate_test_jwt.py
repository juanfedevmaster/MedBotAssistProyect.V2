#!/usr/bin/env python3
"""
Generador de JWT de prueba para MedBot Assistant
"""

import jwt
from datetime import datetime, timedelta
import json

def generate_test_jwt():
    # Generate a test JWT with the user 'jperez'
    
    # JWT Configuration (must match .env)
    SECRET = "a1B2c3D4e5F6g7H8i9J0kLmNoPqRsTuVwXyZ1234567890==!"
    ISSUER = "MedBotAssist"
    AUDIENCE = "MedBotAssistUsers"
    EXPIRATION_MINUTES = 60
    
    # Payload the token
    now = datetime.utcnow()
    payload = {
        "iss": ISSUER,                              # Issuer
        "aud": AUDIENCE,                            # Audience  
        "sub": "user_12345",                        # Subject (user ID)
        "userid": "jperez",                         # ← User ID for JWT service validation
        "name": "jperez",                           # ← Username for SQL query
        "email": "jperez@medbot.com",
        "role": "doctor",
        "permissions": ["UseAgent"],                # ← Required permission for vectorization endpoints
        "sasToken": "sv=2025-07-05&se=2025-07-31T18%3A33%3A30Z&sr=c&sp=rcwdl&sig=P05relRydQUZkDSI6hmXi4UzpInlDTUEFOVmpbNPBp0%3D",  # ← Real SAS token for blob storage
        "iat": now,                                 # Issued at
        "exp": now + timedelta(minutes=EXPIRATION_MINUTES)  # Expiration
    }
    
    # Generate token
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    
    return token, payload

def main():
    print("🔐 JWT Generator for MedBot Assistant")
    print("=" * 60)
    
    try:
        token, payload = generate_test_jwt()

        print("✅ JWT generated successfully!")
        print(f"\n📋 Token payload:")
        print(json.dumps(payload, indent=2, default=str))
        
        print(f"\n🎫 Token JWT:")
        print(f"Bearer {token}")
        
        print(f"\n📝 For use in Postman/Curl:")
        print(f"Authorization: Bearer {token}")

        print(f"\n🧪 Test curl commands:")
        print(f'# List files in blob storage:')
        print(f'curl -X GET "http://localhost:8000/api/v1/blob/files" \\')
        print(f'  -H "Authorization: Bearer {token}"')
        
        print(f'\n# Download specific file:')
        print(f'curl -X GET "http://localhost:8000/api/v1/blob/files/example.pdf" \\')
        print(f'  -H "Authorization: Bearer {token}" \\')
        print(f'  --output "downloaded_file.pdf"')
        
        print(f'\n# Check if file exists:')
        print(f'curl -X GET "http://localhost:8000/api/v1/blob/files/example.pdf/exists" \\')
        print(f'  -H "Authorization: Bearer {token}"')

        print(f"\n💡 This token includes:")
        print(f"  - Username: 'jperez' (for database queries)")  
        print(f"  - SAS Token: For blob storage access")
        print(f"⏰ Token valid for: 60 minutes")
        print(f"🗂️  Blob container: instructions-files")
        print(f"🌐 Blob storage: https://strmedbotassist.blob.core.windows.net")

    except Exception as e:
        print(f"❌ Error generating JWT: {e}")

if __name__ == "__main__":
    main()
