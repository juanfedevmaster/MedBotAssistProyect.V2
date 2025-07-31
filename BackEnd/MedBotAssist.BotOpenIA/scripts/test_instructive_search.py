"""
Script de prueba para las herramientas de búsqueda de instructivos
"""
import sys
import os
import requests
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_instructive_search_endpoints():
    """Prueba los endpoints de búsqueda de instructivos"""
    base_url = "http://localhost:8000/api/v1/vectorization"
    
    print("🧪 Testing Instructive Search Endpoints\n")
    
    # Test 1: Get available instructives
    print("1️⃣ Testing: Get Available Instructives")
    try:
        response = requests.get(f"{base_url}/available-instructives")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: Found {data.get('total_files', 0)} instructives")
            if data.get('instructives'):
                for doc in data['instructives'][:3]:  # Show first 3
                    print(f"   • {doc['filename']} ({doc['file_type']}) - {doc['chunks_count']} chunks")
        else:
            print(f"❌ Error: {response.text}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Search instructives
    print("2️⃣ Testing: Search Instructives")
    search_queries = [
        "medication administration",
        "wound care",
        "insulin protocol",
        "patient safety procedures"
    ]
    
    for query in search_queries:
        print(f"\n🔍 Searching: '{query}'")
        try:
            response = requests.get(
                f"{base_url}/search-instructives",
                params={
                    "query": query,
                    "max_results": 3,
                    "min_similarity": 0.6
                }
            )
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Found {data.get('total_found', 0)} results")
                    if data.get('response'):
                        print(f"Response: {data['response'][:200]}...")
                    if data.get('sources'):
                        print(f"Sources: {', '.join(data['sources'])}")
                else:
                    print(f"ℹ️ {data.get('message', 'No results found')}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Search by filename (if we have any files)
    print("3️⃣ Testing: Search by Filename")
    try:
        # First get available files
        response = requests.get(f"{base_url}/available-instructives")
        if response.status_code == 200:
            data = response.json()
            if data.get('instructives'):
                filename = data['instructives'][0]['filename']
                print(f"🔍 Searching in file: '{filename}'")
                
                response = requests.get(
                    f"{base_url}/search-by-filename",
                    params={
                        "filename": filename,
                        "query": "procedure"
                    }
                )
                print(f"Status Code: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Found {data.get('total_chunks', 0)} chunks in {filename}")
                    else:
                        print(f"ℹ️ {data.get('message', 'No results found')}")
            else:
                print("ℹ️ No files available to test filename search")
        else:
            print("❌ Could not get available files for filename test")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

def test_agent_with_instructives():
    """Prueba el agente médico con las nuevas herramientas de instructivos"""
    print("\n" + "="*60)
    print("🤖 Testing Medical Agent with Instructive Tools")
    print("="*60 + "\n")
    
    # Generar un token JWT de prueba
    try:
        from scripts.generate_test_jwt import generate_test_jwt
        token = generate_test_jwt()
        print("✅ JWT Token generated successfully")
    except Exception as e:
        print(f"❌ Could not generate JWT token: {e}")
        return
    
    # Test agent queries
    agent_url = "http://localhost:8000/api/v1/agent/chat"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    test_queries = [
        "¿Qué instructivos médicos tienes disponibles?",
        "¿Cómo se administra insulina según los protocolos?",
        "Busca información sobre cuidado de heridas",
        "¿Hay algún protocolo para medicación oral?"
    ]
    
    for query in test_queries:
        print(f"\n💬 Query: '{query}'")
        try:
            response = requests.post(
                agent_url,
                headers=headers,
                json={"message": query}
            )
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Response: {data['response'][:300]}...")
                else:
                    print(f"❌ Agent Error: {data.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.text}")
        except Exception as e:
            print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Instructive Search Tools Test Suite")
    print("=" * 60)
    
    # Test endpoints
    test_instructive_search_endpoints()
    
    # Test agent integration
    test_agent_with_instructives()
    
    print("\n✅ Test suite completed!")
    print("📝 Check the results above to verify functionality")
