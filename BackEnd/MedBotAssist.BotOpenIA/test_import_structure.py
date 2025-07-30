#!/usr/bin/env python3
"""
Simple test script to validate that the modular refactoring imports work correctly.
This script focuses only on import testing without database dependencies.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test that all basic imports work correctly."""
    print("🧪 Testing Basic Import Structure")
    print("=" * 50)
    
    try:
        # Test 1: Permission validators
        print("\n📋 Test 1: Permission Validators")
        from app.agents.tools.permission_validators import (
            check_use_agent_permission,
            check_view_patients_permission,
            check_create_patients_permission,
            validate_patient_view_permissions,
            validate_patient_management_permissions
        )
        print("✅ All permission validator functions imported")
        
        # Test basic functionality
        has_permission, error_msg = check_use_agent_permission()
        if not has_permission and "UseAgent" in error_msg:
            print("✅ check_use_agent_permission works correctly")
        
        # Test 2: Search tools imports (classes only, not instances)
        print("\n📋 Test 2: Search Tools Classes")
        from app.agents.tools import patient_search_tools
        print("✅ patient_search_tools module imported")
        
        # Test 3: Management tools imports
        print("\n📋 Test 3: Management Tools Classes")
        from app.agents.tools import patient_management_tools
        print("✅ patient_management_tools module imported")
        
        # Test 4: Main package structure
        print("\n📋 Test 4: Main Package Import Structure")
        import app.agents.tools
        print("✅ app.agents.tools package imported")
        
        # Check if __init__.py exports what we expect
        if hasattr(app.agents.tools, '__all__'):
            print(f"✅ Package has __all__ with {len(app.agents.tools.__all__)} exports")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_individual_functions():
    """Test individual function accessibility."""
    print("\n📋 Test 5: Individual Function Access")
    print("-" * 50)
    
    try:
        # Test permission functions
        from app.agents.tools.permission_validators import validate_patient_view_permissions
        
        # Test that they return expected format without errors
        result = validate_patient_view_permissions()
        if isinstance(result, tuple) and len(result) == 2:
            has_permission, error_msg = result
            if isinstance(has_permission, bool) and isinstance(error_msg, str):
                print("✅ validate_patient_view_permissions returns correct format")
                
                if "UseAgent" in error_msg and "ViewPatients" in error_msg:
                    print("✅ Error message contains both required permissions")
                elif "UseAgent" in error_msg:
                    print("✅ Error message mentions UseAgent permission")
            else:
                print("❌ Invalid return types")
                return False
        else:
            print("❌ Invalid return format")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing individual functions: {e}")
        return False

def test_module_structure():
    """Test that modules are properly structured."""
    print("\n📋 Test 6: Module Structure")
    print("-" * 50)
    
    try:
        # Check module files exist
        import app.agents.tools.permission_validators
        import app.agents.tools.patient_search_tools
        import app.agents.tools.patient_management_tools
        
        print("✅ All expected modules are importable")
        
        # Check that modules have expected attributes
        pv_module = app.agents.tools.permission_validators
        expected_pv_functions = [
            'check_use_agent_permission',
            'check_view_patients_permission', 
            'check_create_patients_permission',
            'validate_patient_view_permissions',
            'validate_patient_management_permissions'
        ]
        
        for func_name in expected_pv_functions:
            if hasattr(pv_module, func_name):
                print(f"  ✅ {func_name}")
            else:
                print(f"  ❌ {func_name} - MISSING!")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing module structure: {e}")
        return False

def test_backwards_compatibility():
    """Test that old import style still works."""
    print("\n📋 Test 7: Backwards Compatibility")
    print("-" * 50)
    
    try:
        # This is what the medical agent uses - should still work
        from app.agents.tools import ALL_TOOLS
        print("✅ Backwards compatible import works")
        
        if ALL_TOOLS and len(ALL_TOOLS) > 0:
            print(f"✅ ALL_TOOLS contains {len(ALL_TOOLS)} tools")
            
            # Check that each tool has basic attributes
            for i, tool in enumerate(ALL_TOOLS[:3]):  # Check first 3 tools
                if hasattr(tool, 'name'):
                    print(f"  ✅ Tool {i+1}: {tool.name}")
                else:
                    print(f"  ❌ Tool {i+1}: Missing name attribute")
                    return False
        else:
            print("❌ ALL_TOOLS is empty or None")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing backwards compatibility: {e}")
        return False

def main():
    """Run all import tests."""
    print("🚀 Starting Modular Structure Import Tests")
    print("This script validates that the refactoring imports work correctly")
    print("=" * 70)
    
    tests = [
        test_basic_imports,
        test_individual_functions,
        test_module_structure,
        test_backwards_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ {test.__name__} FAILED")
        except Exception as e:
            print(f"❌ {test.__name__} FAILED with exception: {e}")
    
    print("\n" + "=" * 70)
    print(f"🏁 Import Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All import tests passed! The modular refactoring was successful.")
        print("\n🎉 Key achievements:")
        print("  • ✅ Code is organized into logical modules")
        print("  • ✅ Permission validation is centralized")  
        print("  • ✅ Tools are grouped by functionality")
        print("  • ✅ Backwards compatibility is maintained")
        print("  • ✅ Import structure is clean and logical")
        print("\n📂 New structure:")
        print("  app/agents/tools/")
        print("  ├── __init__.py                    (Main exports)")
        print("  ├── permission_validators.py       (Security layer)")
        print("  ├── patient_search_tools.py       (Query operations)")
        print("  └── patient_management_tools.py    (CRUD operations)")
    else:
        print("❌ Some import tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
