#!/usr/bin/env python3
"""
Script para probar la generación de embeddings directamente
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.tools.instructive_search_tools import InstructiveSearchTools
from openai import OpenAI
from app.core.config import settings

def test_embeddings():
    """Probar la generación de embeddings"""
    print("🔢 Testing Embedding Generation")
    print("=" * 50)
    
    try:
        # Probar con OpenAI directo
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        test_text = "caldo de hueso"
        
        print(f"🧪 Testing with text: '{test_text}'")
        print(f"📝 Using model: text-embedding-3-small")
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=test_text
        )
        
        embedding = response.data[0].embedding
        print(f"✅ Direct OpenAI embedding dimensions: {len(embedding)}")
        
        # Probar con las herramientas
        tools = InstructiveSearchTools()
        tool_embedding = tools._generate_embedding(test_text)
        print(f"✅ Tool embedding dimensions: {len(tool_embedding)}")
        
        # Comparar si son iguales
        if len(embedding) == len(tool_embedding):
            print("✅ Embeddings have same dimensions")
            
            # Probar similaridad (primeros 5 valores)
            print(f"📊 Direct embedding preview: {embedding[:5]}")
            print(f"📊 Tool embedding preview: {tool_embedding[:5]}")
        else:
            print("❌ Embeddings have different dimensions!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_embeddings()
