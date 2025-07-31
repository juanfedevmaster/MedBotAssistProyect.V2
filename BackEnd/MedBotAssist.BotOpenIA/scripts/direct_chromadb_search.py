#!/usr/bin/env python3
"""
Script para hacer búsqueda directa en ChromaDB
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from openai import OpenAI

def direct_chromadb_search():
    """Hacer búsqueda directa en ChromaDB"""
    print("🔍 Direct ChromaDB Search")
    print("=" * 50)
    
    try:
        # Inicializar cliente ChromaDB
        client = chromadb.PersistentClient(
            path=settings.VECTOR_DB_PATH,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Obtener colección
        collection = client.get_collection("medical_documents")
        count = collection.count()
        print(f"📊 Collection has {count} documents")
        
        # Obtener todos los documentos para ver qué contenido hay
        all_docs = collection.get()
        print(f"📄 Retrieved {len(all_docs['documents'])} documents")
        
        # Mostrar contenido de los primeros documentos
        for i, doc in enumerate(all_docs['documents'][:2]):
            print(f"\n📝 Document {i+1} preview:")
            print(f"   {doc[:200]}...")
        
        # Hacer búsqueda con embedding manual
        openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        queries = ["caldo de hueso", "preparar caldo", "bone broth", "huesos"]
        
        for query in queries:
            print(f"\n🔍 Searching for: '{query}'")
            
            # Generar embedding
            response = openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = response.data[0].embedding
            print(f"   Generated embedding with {len(query_embedding)} dimensions")
            
            # Buscar en ChromaDB
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=3,
                include=["documents", "metadatas", "distances"]
            )
            
            print(f"   Found {len(results['documents'][0])} results")
            
            if results['documents'][0]:
                for j, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
                    print(f"   Result {j+1} (distance: {distance:.4f}): {doc[:100]}...")
            else:
                print("   No results found")
                
        # Probar con umbral más bajo
        print(f"\n🔍 Testing with lower similarity threshold...")
        query = "preparar"
        response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=10,  # Más resultados
            include=["documents", "metadatas", "distances"]
        )
        
        print(f"   Found {len(results['documents'][0])} results for '{query}':")
        for j, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            print(f"   Result {j+1} (distance: {distance:.4f}): {doc[:150]}...")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    direct_chromadb_search()
