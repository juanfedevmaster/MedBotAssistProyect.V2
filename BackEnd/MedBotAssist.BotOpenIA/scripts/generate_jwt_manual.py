#!/usr/bin/env python3
"""
Simple script to generate JWT using only standard libraries
"""

import base64
import json
import hmac
import hashlib
import time

def base64url_encode(data):
    """Codifica en base64url"""
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, dict):
        data = json.dumps(data, separators=(',', ':')).encode('utf-8')
    
    encoded = base64.urlsafe_b64encode(data).decode('utf-8')
    return encoded.rstrip('=')

def create_jwt_manual():
    # Create a JWT manually without PyJWT
    
    # Header
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }
    
    # Payload
    current_time = int(time.time())
    payload = {
        "iss": "MedBotAssist",
        "aud": "MedBotAssistUsers", 
        "sub": "user_12345",
        "name": "jperez",
        "email": "jperez@medbot.com",
        "role": "doctor",
        "iat": current_time,
        "exp": current_time + 3600  # 1 hora
    }
    
    # Encode header and payload
    encoded_header = base64url_encode(header)
    encoded_payload = base64url_encode(payload)
    
    # Create message for signature
    message = f"{encoded_header}.{encoded_payload}"

    # Create HMAC-SHA256 signature
    secret = "a1B2c3D4e5F6g7H8i9J0kLmNoPqRsTuVwXyZ1234567890==!"
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    encoded_signature = base64url_encode(signature)
    
    # JWT token
    jwt_token = f"{message}.{encoded_signature}"
    
    return jwt_token, payload

def main():
    print("🔐 Generador Manual de JWT para MedBot Assistant")
    print("=" * 60)
    
    try:
        token, payload = create_jwt_manual()
        
        print("✅ JWT successfully generated!")
        print(f"\n📋 Token payload:")
        print(json.dumps(payload, indent=2))

        print(f"\n🎫 Complete JWT token:")
        print(token)

        print(f"\n📝 To use as Authorization header:")
        print(f"Bearer {token}")

        print(f"\n🧪 Test curl command:")
        print(f'curl -X POST "http://localhost:8000/api/v1/agent/permissions" \\')
        print(f'  -H "Authorization: Bearer {token}"')

        print(f"\n💡 This token will request permissions for the user: 'jperez'")
        print(f"⏰ Token valid for: 1 hour")
        
        return token
        
    except Exception as e:
        print(f"❌ Error generating JWT: {e}")
        return None

if __name__ == "__main__":
    main()
