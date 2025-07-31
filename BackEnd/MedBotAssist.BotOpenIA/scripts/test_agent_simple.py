"""
Simple script to test the medical agent with instructional documents
"""
import requests
import json
import os
from pathlib import Path

def get_jwt_token():
    """Get JWT token from environment variable or generate one"""
    token = os.getenv('JWT_TOKEN')
    if token:
        return token.replace('Bearer ', '')  # Remove Bearer prefix if present
    
    print("⚠️  JWT_TOKEN environment variable not set")
    print("💡 Run: python scripts/generate_test_jwt.py")
    print("   Then set the JWT_TOKEN environment variable")
    return None

def test_agent():
    token = get_jwt_token()
    if not token:
        print("❌ No JWT token available. Cannot proceed with tests.")
        return
    
    url = "http://localhost:8000/api/v1/agent/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    queries = [
        "What medical instructional documents do you have available?",
        "Search for information about medication administration",
        "How many patients are in the database?"
    ]
    
    print("💬 Testing Medical Agent with Instructive Tools")
    print("=" * 50)
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        try:
            response = requests.post(
                url,
                headers=headers,
                json={"message": query}
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Response: {data['response'][:500]}...")
                else:
                    print(f"❌ Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    test_agent()
