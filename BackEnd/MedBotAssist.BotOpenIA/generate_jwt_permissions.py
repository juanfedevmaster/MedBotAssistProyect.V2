#!/usr/bin/env python3
"""
Generador de JWT con diferentes niveles de permisos para pruebas
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
    print("🔐 Generador de JWT con Permisos para Pruebas")
    print("=" * 60)
    
    # Scenario 1: Usuario con ViewPatients (acceso completo)
    print("\n📋 Scenario 1: Usuario con ViewPatients")
    token1, payload1 = create_jwt_with_permissions("jperez", ["ViewPatients", "ViewAppointments"])
    print(f"Usuario: jperez")
    print(f"Permisos: {payload1['permissions']}")
    print(f"Token: {token1}")
    
    # Scenario 2: Usuario SIN ViewPatients (acceso restringido)  
    print("\n📋 Scenario 2: Usuario SIN ViewPatients")
    token2, payload2 = create_jwt_with_permissions("mgarcia", ["ViewAppointments", "GenerateSummaries"])
    print(f"Usuario: mgarcia")
    print(f"Permisos: {payload2['permissions']}")
    print(f"Token: {token2}")
    
    # Scenario 3: Usuario sin permisos
    print("\n📋 Scenario 3: Usuario sin permisos")
    token3, payload3 = create_jwt_with_permissions("guest", [])
    print(f"Usuario: guest")
    print(f"Permisos: {payload3['permissions']}")
    print(f"Token: {token3}")
    
    print("\n🧪 Comandos de prueba:")
    print(f'\n✅ Con ViewPatients (debería funcionar):')
    print(f'$token1 = "{token1}"')
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer $token1"; "Content-Type" = "application/json"}} -Body \'{{"message": "¿Cuántos pacientes hay en la base de datos?", "conversation_id": "test1"}}\'')
    
    print(f'\n❌ SIN ViewPatients (debería devolver error de permisos):')
    print(f'$token2 = "{token2}"')
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer $token2"; "Content-Type" = "application/json"}} -Body \'{{"message": "¿Cuántos pacientes hay en la base de datos?", "conversation_id": "test2"}}\'')

if __name__ == "__main__":
    main()
