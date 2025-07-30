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
        "name": "jperez",                           # ← Username for SQL query
        "email": "jperez@medbot.com",
        "role": "doctor",
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

        print(f"\n🧪 Test curl command:")
        print(f'curl -X POST "http://localhost:8000/api/v1/agent/permissions" \\')
        print(f'  -H "Authorization: Bearer {token}" \\')
        print(f'  -H "Content-Type: application/json"')

        print(f"\n💡 This token will seek permissions for the user: 'jperez'")
        print(f"⏰ Token valid for: 60 minutes")

    except Exception as e:
        print(f"❌ Error generating JWT: {e}")

if __name__ == "__main__":
    main()
