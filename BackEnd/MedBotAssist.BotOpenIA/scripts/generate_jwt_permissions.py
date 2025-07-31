#!/usr/bin/env python3
"""
JWT generator with different permission levels for testing
"""

import base64
import json
import hmac
import hashlib
import time

def base64url_encode(data):
    # Codifica en base64url
    if isinstance(data, str):
        data = data.encode('utf-8')
    elif isinstance(data, dict):
        data = json.dumps(data, separators=(',', ':')).encode('utf-8')
    
    encoded = base64.urlsafe_b64encode(data).decode('utf-8')
    return encoded.rstrip('=')

def create_jwt_with_permissions(username, permissions):
    # Create a JWT with specific permissions

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
        "sub": f"user_{username}",
        "name": username,
        "email": f"{username}@medbot.com",
        "permissions": permissions,  # Permission array
        "iat": current_time,
        "exp": current_time + 3600  # 1 hour
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
    print("🔐 JWT Generator with Permissions for Testing")
    print("=" * 60)

    # Scenario 1: User with ViewPatients (full access)
    print("\n📋 Scenario 1: User with ViewPatients")
    token1, payload1 = create_jwt_with_permissions("jperez", ["ViewPatients", "ViewAppointments"])
    print(f"User: jperez")
    print(f"Permissions: {payload1['permissions']}")
    print(f"Token: {token1}")

    # Scenario 2: User WITHOUT ViewPatients (restricted access)
    print("\n📋 Scenario 2: User WITHOUT ViewPatients")
    token2, payload2 = create_jwt_with_permissions("mgarcia", ["ViewAppointments", "GenerateSummaries"])
    print(f"User: mgarcia")
    print(f"Permissions: {payload2['permissions']}")
    print(f"Token: {token2}")

    # Scenario 3: User without permissions
    print("\n📋 Scenario 3: User without permissions")
    token3, payload3 = create_jwt_with_permissions("guest", [])
    print(f"User: guest")
    print(f"Permissions: {payload3['permissions']}")
    print(f"Token: {token3}")

    print("\n🧪 Test commands:")
    print(f'\n✅ With ViewPatients (should work):')
    print(f'$token1 = "{token1}"')
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer $token1"; "Content-Type" = "application/json"}} -Body \'{{"message": "¿Cuántos pacientes hay en la base de datos?", "conversation_id": "test1"}}\'')
    
    print(f'\n❌ WITHOUT ViewPatients (should return permission error):')
    print(f'$token2 = "{token2}"')
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer $token2"; "Content-Type" = "application/json"}} -Body \'{{"message": "¿Cuántos pacientes hay en la base de datos?", "conversation_id": "test2"}}\'')

if __name__ == "__main__":
    main()
