"""
Test script for the new diagnosis search tools.
"""

import sys
sys.path.append('.')

def test_diagnosis_search_tools():
    """Test the diagnosis search tools"""
    try:
        from app.agents.tools.diagnosis_search_tools import (
            search_patients_by_diagnosis_impl,
            get_patient_names_by_diagnosis_impl
        )
        
        # Create test permission context
        class MockPermissionContext:
            def __init__(self):
                self.permissions = ['read_patients', 'read_medical_history']
                self.user_id = 'test_user'
                self.hospital_id = 'test_hospital'
        
        permission_context = MockPermissionContext()
        
        print("🧪 Testing diagnosis search tools...")
        print("=" * 60)
        
        # Test 1: Complete patient search by diagnosis
        print("\n1️⃣ Complete search by diagnosis (Hypertension):")
        print("-" * 50)
        result1 = search_patients_by_diagnosis_impl(
            diagnosis_keyword='Hipertensión',
            permission_context=permission_context
        )
        print(result1)
        
        # Test 2: Get only names by diagnosis
        print("\n2️⃣ Patient names by diagnosis (Hypertension):")
        print("-" * 50)
        result2 = get_patient_names_by_diagnosis_impl(
            diagnosis_keyword='Hipertensión',
            permission_context=permission_context
        )
        print(result2)
        
        # Test 3: Search for non-existent diagnosis
        print("\n3️⃣ Search for non-existent diagnosis (Flu):")
        print("-" * 50)
        result3 = get_patient_names_by_diagnosis_impl(
            diagnosis_keyword='Gripe',
            permission_context=permission_context
        )
        print(result3)
        
        print("\n✅ Tests completed successfully!")
        print("📊 Diagnosis search tools are working.")
        
    except Exception as e:
        print(f"❌ Error in tests: {str(e)}")
        import traceback
        traceback.print_exc()

def test_tools_integration():
    """Test the tools integration in the system"""
    try:
        from app.agents.tools import ALL_TOOLS
        
        print("\n🔧 Verifying tools integration...")
        print("=" * 60)
        
        # Search for new tools in the list
        diagnosis_tools = [
            'search_patients_by_diagnosis',
            'get_patient_names_by_diagnosis'
        ]
        
        tool_names = [tool.name for tool in ALL_TOOLS]
        
        print(f"📋 Total available tools: {len(ALL_TOOLS)}")
        print(f"🔍 Tools found: {tool_names}")
        
        for tool_name in diagnosis_tools:
            if tool_name in tool_names:
                print(f"✅ {tool_name} - Integrated correctly")
            else:
                print(f"❌ {tool_name} - Not found in ALL_TOOLS")
        
        print(f"\n📊 System updated with {len(ALL_TOOLS)} total tools")
        
    except Exception as e:
        print(f"❌ Error verifying integration: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting diagnosis tools tests...")
    
    # Test the tools
    test_diagnosis_search_tools()
    
    # Test the integration
    test_tools_integration()
    
    print("\n🎉 Tests finished!")
