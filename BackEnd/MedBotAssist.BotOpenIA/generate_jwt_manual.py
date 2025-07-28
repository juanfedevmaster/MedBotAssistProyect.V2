#!/usr/bin/env python3
"""
Script simple para generar JWT usando solo bibliotecas estándar
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
    """Crea un JWT manualmente sin PyJWT"""
    
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
    print("🔐 Generador Manual de JWT para MedBot Assistant")
    print("=" * 60)
    
    try:
        token, payload = create_jwt_manual()
        
        print("✅ JWT generado exitosamente!")
        print(f"\n📋 Payload del token:")
        print(json.dumps(payload, indent=2))
        
        print(f"\n🎫 Token JWT completo:")
        print(token)
        
        print(f"\n📝 Para usar como Authorization header:")
        print(f"Bearer {token}")
        
        print(f"\n🧪 Comando curl de prueba:")
        print(f'curl -X POST "http://localhost:8000/api/v1/agent/permissions" \\')
        print(f'  -H "Authorization: Bearer {token}"')
        
        print(f"\n💡 Este token buscará permisos para el usuario: 'jperez'")
        print(f"⏰ Token válido por: 1 hora")
        
        return token
        
    except Exception as e:
        print(f"❌ Error generando JWT: {e}")
        return None

if __name__ == "__main__":
    main()
