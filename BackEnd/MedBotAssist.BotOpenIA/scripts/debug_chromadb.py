#!/usr/bin/env python3
"""
Script de debug para verificar el estado de ChromaDB y documentos vectorizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# SQLite fix for Azure App Service BEFORE ChromaDB imports
try:
    import sqlite_fix
except ImportError:
    pass

import chromadb
from chromadb.config import Settings
from app.agents.tools.instructive_search_tools import InstructiveSearchTools

def debug_chromadb():
    print("🔍 CHROMADB DEBUG SCRIPT")
    print("=" * 50)
    
    try:
        # 1. Inicializar cliente ChromaDB directamente
        print("1. Inicializando cliente ChromaDB...")
        chroma_client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 2. Listar colecciones
        print("2. Listando colecciones disponibles...")
        collections = chroma_client.list_collections()
        print(f"   Colecciones encontradas: {len(collections)}")
        for col in collections:
            print(f"   - {col.name} (metadata: {col.metadata})")
        
        # 3. Verificar colección medical_documents
        print("3. Verificando colección 'medical_documents'...")
        try:
            collection = chroma_client.get_collection("medical_documents")
            count = collection.count()
            print(f"   ✅ Colección encontrada con {count} documentos")
            
            if count > 0:
                # 4. Obtener algunos documentos de muestra
                print("4. Obteniendo documentos de muestra...")
                sample = collection.peek(limit=5)
                print(f"   IDs: {sample.get('ids', [])}")
                print(f"   Metadatos: {sample.get('metadatas', [])}")
                
                # 5. Hacer query simple
                print("5. Haciendo query de prueba...")
                if sample.get('documents') and len(sample['documents']) > 0:
                    # Usar el primer documento como query
                    first_doc = sample['documents'][0][:50] + "..."
                    print(f"   Query text: '{first_doc}'")
                    
                    results = collection.query(
                        query_texts=[first_doc],
                        n_results=3,
                        include=['documents', 'metadatas', 'distances']
                    )
                    
                    print(f"   Resultados encontrados: {len(results.get('documents', [[]])[0])}")
                    for i, (doc, meta) in enumerate(zip(
                        results.get('documents', [[]])[0][:2], 
                        results.get('metadatas', [[]])[0][:2]
                    )):
                        print(f"   - Resultado {i+1}: {meta.get('filename', 'unknown')} ({doc[:100]}...)")
            
        except Exception as e:
            print(f"   ❌ Error accediendo a colección: {e}")
        
        # 6. Probar herramientas de búsqueda
        print("6. Probando herramientas de búsqueda...")
        tools = InstructiveSearchTools()
        
        print("   Probando get_available_instructives()...")
        available = tools.get_available_instructives()
        print(f"   Resultado: {available}")
        
        if available.get('success') and available.get('total_files', 0) > 0:
            print("   Probando búsqueda de contenido...")
            search_result = tools.search_instructive_information("medical procedure")
            print(f"   Búsqueda exitosa: {search_result.get('success', False)}")
            print(f"   Resultados encontrados: {search_result.get('total_found', 0)}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_chromadb()
