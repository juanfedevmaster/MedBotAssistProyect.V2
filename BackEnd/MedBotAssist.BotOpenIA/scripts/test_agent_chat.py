#!/usr/bin/env python3
"""
Script para probar el chat del agente médico
"""
import requests
import json

# Token JWT con SAS token actualizado  
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJNZWRCb3RBc3Npc3QiLCJhdWQiOiJNZWRCb3RBc3Npc3RVc2VycyIsInN1YiI6InVzZXJfMTIzNDUiLCJ1c2VyaWQiOiJqcGVyZXoiLCJuYW1lIjoianBlcmV6IiwiZW1haWwiOiJqcGVyZXpAbWVkYm90LmNvbSIsInJvbGUiOiJkb2N0b3IiLCJwZXJtaXNzaW9ucyI6WyJVc2VBZ2VudCJdLCJzYXNUb2tlbiI6InN2PTIwMjUtMDctMDUmc2U9MjAyNS0wNy0zMVQxOCUzQTMzJTNBMzBaJnNyPWMmc3A9cmN3ZGwmc2lnPVAwNXJlbFJ5ZFFVWmtEU0k2aG1YaTRVenBJbmxEVFVFRk9WbXBiTlBCcDAlM0QiLCJpYXQiOjE3NTM5ODc1OTIsImV4cCI6MTc1Mzk5MTE5Mn0.xLu4J6_brF8YrOW1H21s8h4AfJ02qWlHd5GFwq6mqFg"

def test_agent_chat():
    """Probar el chat del agente médico"""
    url = "http://localhost:8000/api/v1/agent/chat"
    
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "message": "Busca en los instructivos médicos información sobre cómo preparar caldo de hueso",
        "conversation_id": "test_instructives"
    }
    
    print("🤖 Testing Medical Agent Chat")
    print("=" * 50)
    print(f"URL: {url}")
    print(f"Message: {payload['message']}")
    print()
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"Response: {result.get('response', 'No response field')}")
            print(f"Agent used tools: {result.get('agent_used_tools', False)}")
            print(f"Available tools: {result.get('available_tools', [])}")
            print(f"Status: {result.get('status', 'No status')}")
            
            # Si la respuesta menciona instructivos, mostrar más detalles
            if "instructivo" in result.get('response', '').lower():
                print("\n📋 Response mentions instructives!")
            
        else:
            print("❌ ERROR!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_agent_chat()
