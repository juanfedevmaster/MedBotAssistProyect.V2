#!/usr/bin/env python3
"""
Script para recrear la colección de ChromaDB desde cero
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings

async def recreate_chromadb_collection():
    """Recrear la colección de ChromaDB desde cero"""
    print("🔄 Recreating ChromaDB Collection")
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
        print(f"✅ ChromaDB client initialized at: {settings.VECTOR_DB_PATH}")
        
        # Listar colecciones existentes
        collections = client.list_collections()
        print(f"📋 Found {len(collections)} existing collections:")
        for collection in collections:
            print(f"   - {collection.name}")
        
        # Eliminar colección médica si existe
        try:
            client.delete_collection("medical_documents")
            print("🗑️ Deleted existing 'medical_documents' collection")
        except Exception as e:
            print(f"ℹ️ No existing 'medical_documents' collection to delete: {e}")
        
        # Crear nueva colección
        collection = client.create_collection(
            name="medical_documents",
            metadata={"description": "Vectorized medical instructional documents"}
        )
        print("✅ Created new 'medical_documents' collection")
        
        # Verificar que está vacía
        count = collection.count()
        print(f"📊 Collection document count: {count}")
        
        # Ahora vamos a agregar nuestro contenido local
        from app.services.vectorization_manager import VectorizationManager
        
        # Leer el archivo local
        file_path = "temp_bone_broth_instructions.txt"
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"\n📄 Loading content: {len(content)} characters")
        
        # Inicializar vectorization manager
        vm = VectorizationManager()
        
        # Procesar el texto
        chunks = vm._chunk_text(content)
        print(f"📄 Created {len(chunks)} chunks")
        
        # Generar embeddings
        embeddings = await vm._generate_embeddings(chunks)
        print(f"🔢 Generated {len(embeddings)} embeddings")
        
        if embeddings and len(embeddings[0]) > 0:
            print(f"✅ Embedding dimensions: {len(embeddings[0])}")
        
        # Preparar datos para ChromaDB
        import hashlib
        from datetime import datetime
        
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
                'etag': '"manual_upload_v2"',
                'last_modified': datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'vectorization_timestamp': datetime.now().isoformat()
            }
            metadatas.append(metadata)
        
        # Agregar a la nueva colección
        collection.add(
            ids=chunk_ids,
            documents=chunks,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        print(f"✅ Added {len(chunks)} chunks to new collection")
        
        # Verificar
        final_count = collection.count()
        print(f"📊 Final collection document count: {final_count}")
        
        print("\n✅ ChromaDB collection recreated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    await recreate_chromadb_collection()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
