#!/usr/bin/env python3
"""
Script para generar JWT con el SAS token actualizado
"""
import jwt
from datetime import datetime, timedelta

# Configuración del JWT
SECRET_KEY = "your-secret-key-here-make-it-long-and-random-for-production"
ALGORITHM = "HS256"

def generate_jwt_with_updated_sas():
    """Generar JWT con el SAS token actualizado"""
    print("🔐 JWT Generator with Updated SAS Token")
    print("=" * 50)
    
    # SAS token actualizado
    sas_token = "sv=2025-07-05&se=2025-07-31T20%3A00%3A21Z&sr=c&sp=rcwdl&sig=o%2Bi0CYM8sdgpBWBtwMZJq4LtLrFkeqkiUabrRLHpNFo%3D"
    
    # Payload del JWT
    now = datetime.utcnow()
    payload = {
        "iss": "MedBotAssist",
        "aud": "MedBotAssistUsers", 
        "sub": "user_12345",
        "userid": "jperez",
        "name": "jperez",
        "email": "jperez@medbot.com",
        "role": "doctor",
        "permissions": ["UseAgent"],
        "sasToken": sas_token,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=2)).timestamp())  # Válido por 2 horas
    }
    
    # Generar token
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    
    print("✅ JWT generated successfully!")
    print(f"📋 SAS Token expires: 2025-07-31T20:00:21Z")
    print(f"📋 JWT expires: {datetime.fromtimestamp(payload['exp']).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n🎫 Token:")
    print(f"Bearer {token}")
    
    return token

if __name__ == "__main__":
    generate_jwt_with_updated_sas()
