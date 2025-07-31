#!/usr/bin/env python3
"""
Script para probar directamente las herramientas de búsqueda de instructivos
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.agents.tools.instructive_search_tools import InstructiveSearchTools

def test_instructive_tools():
    """Probar las herramientas de búsqueda de instructivos"""
    print("🔧 Testing Instructive Search Tools")
    print("=" * 50)
    
    try:
        # Configurar contexto de permisos ANTES de inicializar las herramientas
        from app.services.permission_context import permission_context
        permission_context.set_user_context("test_user", ["UseAgent", "ViewPatients"])
        print("✅ Permission context set")
        
        # Inicializar las herramientas
        tools = InstructiveSearchTools()
        print("✅ InstructiveSearchTools initialized")
        
        # Probar get_available_instructives
        print("\n1. Testing get_available_instructives...")
        available = tools.get_available_instructives()
        print(f"Available instructives: {available}")
        
        # Probar search_instructive_information
        print("\n2. Testing search_instructive_information with 'caldo de hueso'...")
        search_result = tools.search_instructive_information("caldo de hueso")
        print(f"Search result: {search_result}")
        
        # Probar con otros términos
        print("\n3. Testing search_instructive_information with 'preparación'...")
        search_result2 = tools.search_instructive_information("preparación")
        print(f"Search result 2: {search_result2}")
        
        # Probar con términos en inglés
        print("\n4. Testing search_instructive_information with 'bone broth'...")
        search_result3 = tools.search_instructive_information("bone broth")
        print(f"Search result 3: {search_result3}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_instructive_tools()
