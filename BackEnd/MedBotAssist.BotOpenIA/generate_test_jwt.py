#!/usr/bin/env python3
"""
Script para generar un JWT de prueba para validar la extracción de permisos.
"""

import jwt
from datetime import datetime, timedelta
import json

def generate_test_jwt():
    """Genera un JWT de prueba con el usuario 'jperez'"""
    
    # Configuración JWT (debe coincidir con .env)
    SECRET = "a1B2c3D4e5F6g7H8i9J0kLmNoPqRsTuVwXyZ1234567890==!"
    ISSUER = "MedBotAssist"
    AUDIENCE = "MedBotAssistUsers"
    EXPIRATION_MINUTES = 60
    
    # Payload del token
    now = datetime.utcnow()
    payload = {
        "iss": ISSUER,                              # Issuer
        "aud": AUDIENCE,                            # Audience  
        "sub": "user_12345",                        # Subject (user ID)
        "name": "jperez",                           # ← Username para la consulta SQL
        "email": "jperez@medbot.com",
        "role": "doctor",
        "iat": now,                                 # Issued at
        "exp": now + timedelta(minutes=EXPIRATION_MINUTES)  # Expiration
    }
    
    # Generar token
    token = jwt.encode(payload, SECRET, algorithm="HS256")
    
    return token, payload

def main():
    print("🔐 Generador de JWT de Prueba para MedBot Assistant")
    print("=" * 60)
    
    try:
        token, payload = generate_test_jwt()
        
        print("✅ JWT generado exitosamente!")
        print(f"\n📋 Payload del token:")
        print(json.dumps(payload, indent=2, default=str))
        
        print(f"\n🎫 Token JWT:")
        print(f"Bearer {token}")
        
        print(f"\n📝 Para usar en Postman/Curl:")
        print(f"Authorization: Bearer {token}")
        
        print(f"\n🧪 Comando curl de prueba:")
        print(f'curl -X POST "http://localhost:8000/api/v1/agent/permissions" \\')
        print(f'  -H "Authorization: Bearer {token}" \\')
        print(f'  -H "Content-Type: application/json"')
        
        print(f"\n💡 Este token buscará permisos para el usuario: 'jperez'")
        print(f"⏰ Token válido por: 60 minutos")
        
    except Exception as e:
        print(f"❌ Error generando JWT: {e}")

if __name__ == "__main__":
    main()
