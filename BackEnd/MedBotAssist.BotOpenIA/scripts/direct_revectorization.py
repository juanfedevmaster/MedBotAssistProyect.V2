#!/usr/bin/env python3
"""
Script para revectorizar directamente sin depender de SAS tokens
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vectorization_manager import VectorizationManager
from app.core.config import settings

async def direct_revectorization():
    """Revectorizar directamente usando el vectorization manager"""
    print("🔄 Direct Revectorization Script")
    print("=" * 50)
    
    try:
        # Inicializar el vectorization manager
        vm = VectorizationManager()
        print("✅ VectorizationManager initialized")
        
        # Simular archivos que sabemos que están en blob storage
        files_to_process = [
            "Ketogenic_Diet_Instructive.pdf",
            "Instructional_Bone_Ball_Instructions.pdf"
        ]
        
        # SAS token (puedes actualizar esto si es necesario)
        sas_token = "sv=2025-07-05&se=2025-07-31T18%3A33%3A30Z&sr=c&sp=rcwdl&sig=P05relRydQUZkDSI6hmXi4UzpInlDTUEFOVmpbNPBp0%3D"
        
        total_processed = 0
        total_chunks = 0
        
        for filename in files_to_process:
            try:
                print(f"\n📄 Processing: {filename}")
                result = await vm.vectorize_file(filename, sas_token)
                
                if result['success']:
                    chunks = result['chunks_created']
                    total_processed += 1
                    total_chunks += chunks
                    print(f"   ✅ Success: {chunks} chunks created")
                else:
                    print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"   ❌ Error processing {filename}: {e}")
        
        print(f"\n📊 Summary:")
        print(f"   Files processed: {total_processed}/{len(files_to_process)}")
        print(f"   Total chunks created: {total_chunks}")
        
        if total_processed > 0:
            print("\n🔍 Testing search after revectorization...")
            from app.agents.tools.instructive_search_tools import InstructiveSearchTools
            
            # Simular el contexto de permisos
            from app.services.permission_context import permission_context
            permission_context.set_user_context("test_user", ["UseAgent"])
            
            tools = InstructiveSearchTools()
            
            # Probar búsqueda
            search_result = tools.search_instructive_information("caldo de hueso")
            print(f"   Search result success: {search_result.get('success', False)}")
            if search_result.get('success'):
                print(f"   Results found: {len(search_result.get('results', []))}")
            else:
                print(f"   Search error: {search_result.get('error', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(direct_revectorization())
