#!/usr/bin/env python3
"""
JWT generator with ManagePatients permissions to test the new tool
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
    print("JWT generator with ManagePatients permissions")
    print("=" * 60)
    
    # Scenario 1: User with ManagePatients to create patients
    print("\n📋 Scenario 1: User with ManagePatients")
    token1, payload1 = create_jwt_with_permissions("admin", ["ManagePatients", "ViewPatients"])
    print(f"User: admin")
    print(f"Permissions: {payload1['permissions']}")
    print(f"Token: {token1}")

    # Scenario 2: User WITHOUT ManagePatients (can only view)
    print("\n📋 Scenario 2: User WITHOUT ManagePatients")
    token2, payload2 = create_jwt_with_permissions("viewer", ["ViewPatients"])
    print(f"User: viewer")
    print(f"Permissions: {payload2['permissions']}")
    print(f"Token: {token2}")

    print("\n🧪 PowerShell test commands:")
    print(f'\n✅ With ManagePatients (should create patient):')
    print(f'$token1 = "{token1}"')
    print(f'''$body1 = @{{
        message = "Create a new patient with the name 'Carlos Rodríguez', ID '98765432', date of birth '1992-03-20T00:00:00.000Z', age 31, phone number '+57-302-555-1234' and email 'carlos.rodriguez@email.com'."
        conversation_id = "test_create_patient"
    }} | ConvertTo-Json''')
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer $token1"; "Content-Type" = "application/json"}} -Body $body1')

    print(f'\n❌ WITHOUT ManagePatients (should return permission error):')
    print(f'$token2 = "{token2}"')
    print(f'''$body2 = @{{
        message = "Create a new patient with the name 'Ana López', ID '11223344', date of birth '1995-08-15T00:00:00.000Z', age 28, phone number '+57-305-444-5555' and email 'ana.lopez@email.com'."
        conversation_id = "test_create_patient_denied"
    }} | ConvertTo-Json''')
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer $token2"; "Content-Type" = "application/json"}} -Body $body2')

if __name__ == "__main__":
    main()
