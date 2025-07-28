#!/usr/bin/env python3
"""
Generador de JWT con permisos ManagePatients para probar la nueva herramienta
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

def create_jwt_with_permissions(username, permissions):
    """Crea un JWT con permisos específicos"""
    
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
        "permissions": permissions,  # Array de permisos
        "iat": current_time,
        "exp": current_time + 3600  # 1 hora
    }
    
    # Codificar header y payload
    encoded_header = base64url_encode(header)
    encoded_payload = base64url_encode(payload)
    
    # Crear mensaje para firma
    message = f"{encoded_header}.{encoded_payload}"
    
    # Crear firma HMAC-SHA256
    secret = "a1B2c3D4e5F6g7H8i9J0kLmNoPqRsTuVwXyZ1234567890==!"
    signature = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).digest()
    
    encoded_signature = base64url_encode(signature)
    
    # JWT completo
    jwt_token = f"{message}.{encoded_signature}"
    
    return jwt_token, payload

def main():
    print("🔐 Generador de JWT con Permisos ManagePatients")
    print("=" * 60)
    
    # Scenario 1: Usuario con ManagePatients para crear pacientes
    print("\n📋 Scenario 1: Usuario con ManagePatients")
    token1, payload1 = create_jwt_with_permissions("admin", ["ManagePatients", "ViewPatients"])
    print(f"Usuario: admin")
    print(f"Permisos: {payload1['permissions']}")
    print(f"Token: {token1}")
    
    # Scenario 2: Usuario SIN ManagePatients (solo puede ver)
    print("\n📋 Scenario 2: Usuario SIN ManagePatients")
    token2, payload2 = create_jwt_with_permissions("viewer", ["ViewPatients"])
    print(f"Usuario: viewer")
    print(f"Permisos: {payload2['permissions']}")
    print(f"Token: {token2}")
    
    print("\n🧪 Comandos de prueba PowerShell:")
    print(f'\n✅ Con ManagePatients (debería crear el paciente):')
    print(f'$token1 = "{token1}"')
    print(f'''$body1 = @{{
    message = "Crea un nuevo paciente con el nombre 'Carlos Rodríguez', identificación '98765432', fecha de nacimiento '1992-03-20T00:00:00.000Z', edad 31, teléfono '+57-302-555-1234' y email 'carlos.rodriguez@email.com'"
    conversation_id = "test_create_patient"
}} | ConvertTo-Json''')
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer $token1"; "Content-Type" = "application/json"}} -Body $body1')
    
    print(f'\n❌ SIN ManagePatients (debería devolver error de permisos):')
    print(f'$token2 = "{token2}"')
    print(f'''$body2 = @{{
    message = "Crea un nuevo paciente con el nombre 'Ana López', identificación '11223344', fecha de nacimiento '1995-08-15T00:00:00.000Z', edad 28, teléfono '+57-305-444-5555' y email 'ana.lopez@email.com'"
    conversation_id = "test_create_patient_denied"
}} | ConvertTo-Json''')
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer $token2"; "Content-Type" = "application/json"}} -Body $body2')

if __name__ == "__main__":
    main()
