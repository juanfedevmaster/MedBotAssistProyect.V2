"""
Genera un JWT token completo para probar el agente con instructivos
"""
import jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

def generate_complete_jwt():
    """Genera un JWT token con todos los permisos necesarios"""
    
    # Configuración JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")
    JWT_ISSUER = os.getenv("JWT_ISSUER", "MedBotAssist")
    JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "MedBotAssistUsers")
    JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    
    now = datetime.now()
    expiration = now + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    
    # Payload completo con todos los permisos
    payload = {
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "sub": "user_jperez",  # Este debe coincidir con el user_id esperado
        "userid": "jperez",    # ✅ Campo correcto que busca el JWT service
        "name": "jperez",
        "email": "jperez@medbot.com",
        "role": "doctor",
        "permissions": [
            "UseAgent",           # ✅ Permiso principal para usar el agente
            "ViewPatients",       # ✅ Para consultar pacientes
            "ManagePatients",     # ✅ Para crear pacientes
            "ViewAppointments",   # ✅ Para ver citas
            "GenerateSummaries"   # ✅ Para generar resúmenes
        ],
        "iat": int(now.timestamp()),
        "exp": int(expiration.timestamp())
    }
    
    # Generar el token
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    
    print("🔐 JWT Token Generator - Complete Permissions")
    print("=" * 60)
    print(f"✅ Token generated successfully!")
    print(f"📋 Token payload:")
    for key, value in payload.items():
        if key in ['iat', 'exp']:
            # Convertir timestamps a fecha legible
            dt = datetime.fromtimestamp(value)
            print(f"  {key}: {value} ({dt.strftime('%Y-%m-%d %H:%M:%S')})")
        else:
            print(f"  {key}: {value}")
    
    print(f"\n🎫 Complete Token:")
    print(f"Bearer {token}")
    
    print(f"\n📝 For use in scripts:")
    print(f'TOKEN = "{token}"')
    
    print(f"\n🧪 Test command:")
    print(f'Invoke-WebRequest -Uri "http://localhost:8000/api/v1/agent/chat" -Method POST -Headers @{{"Authorization" = "Bearer {token}"; "Content-Type" = "application/json"}} -Body \'{{"message": "¿Qué instructivos médicos tienes disponibles?", "conversation_id": "test_instructives"}}\'')
    
    return token

if __name__ == "__main__":
    generate_complete_jwt()
