#!/usr/bin/env python3
"""
Script para vectorizar contenido local directamente en ChromaDB
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vectorization_manager import VectorizationManager
from app.core.config import settings
import hashlib
from datetime import datetime

async def vectorize_local_content():
    """Vectorizar contenido local directamente"""
    print("🔄 Local Content Vectorization")
    print("=" * 50)
    
    try:
        # Leer el archivo local
        file_path = "temp_bone_broth_instructions.txt"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📄 Content loaded: {len(content)} characters")
        
        # Inicializar el vectorization manager
        vm = VectorizationManager()
        print("✅ VectorizationManager initialized")
        
        # Procesar el texto (dividir en chunks)
        chunks = vm._chunk_text(content)
        print(f"📄 Created {len(chunks)} chunks")
        
        # Generar embeddings
        embeddings = await vm._generate_embeddings(chunks)
        print(f"🔢 Generated {len(embeddings)} embeddings")
        
        if embeddings and len(embeddings[0]) > 0:
            print(f"✅ Embedding dimensions: {len(embeddings[0])}")
        
        # Preparar metadatos
        chunk_ids = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
            chunk_id = f"Instructional_Bone_Ball_Instructions.pdf_{i}_{chunk_hash}"
            chunk_ids.append(chunk_id)
            
            metadata = {
                'filename': 'Instructional_Bone_Ball_Instructions.pdf',
                'file_type': 'application/pdf',
                'file_size': len(content),
                'chunk_index': i,
                'total_chunks': len(chunks),
                'etag': '"manual_upload"',
                'last_modified': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'vectorization_timestamp': datetime.now().isoformat()
            }
            metadatas.append(metadata)
        
        # Agregar a ChromaDB
        vm.collection.add(
            ids=chunk_ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(chunks)} chunks to ChromaDB")
        
        # Probar búsqueda inmediatamente
        print("\n🔍 Testing search immediately...")
        from app.agents.tools.instructive_search_tools import InstructiveSearchTools
        
        # Simular el contexto de permisos
        from app.services.permission_context import permission_context
        permission_context.set_user_context("test_user", ["UseAgent"])
        
        tools = InstructiveSearchTools()
        
        # Probar búsqueda
        test_queries = [
            "caldo de hueso",
            "como preparar caldo",
            "bone broth preparation",
            "preparación inicial"
        ]
        
        for query in test_queries:
            print(f"\n   Testing query: '{query}'")
            search_result = tools.search_instructive_information(query)
            if search_result.get('success'):
                results = search_result.get('results', [])
                print(f"   ✅ Success: {len(results)} results found")
                if results:
                    print(f"   First result preview: {results[0][:100]}...")
            else:
                print(f"   ❌ Failed: {search_result.get('error', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(vectorize_local_content())
