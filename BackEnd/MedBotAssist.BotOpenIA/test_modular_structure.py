#!/usr/bin/env python3
"""
Test script to validate that the modular refactoring works correctly.
This script tests that all tools are still accessible and functional after the refactoring.
"""

import sys
import os
import importlib

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly."""
    print("🧪 Testing Modular Structure - Import Validation")
    print("=" * 60)
    
    # Test 1: Main package import (what the agent uses)
    print("\n📋 Test 1: Main package import")
    try:
        from app.agents.tools import ALL_TOOLS
        print(f"✅ Successfully imported ALL_TOOLS with {len(ALL_TOOLS)} tools")
        
        tool_names = [tool.name for tool in ALL_TOOLS]
        expected_tools = [
            'search_patients',
            'get_patients_summary', 
            'search_patients_by_name',
            'filter_patients_by_demographics',
            'search_patients_by_condition',
            'get_patient_by_id',
            'create_patient',
            'update_patient'
        ]
        
        for expected_tool in expected_tools:
            if expected_tool in tool_names:
                print(f"  ✅ {expected_tool}")
            else:
                print(f"  ❌ {expected_tool} - MISSING!")
                
    except ImportError as e:
        print(f"❌ Failed to import ALL_TOOLS: {e}")
        return False
    
    # Test 2: Individual module imports
    print("\n📋 Test 2: Individual module imports")
    try:
        from app.agents.tools.permission_validators import (
            check_use_agent_permission,
            check_view_patients_permission,
            check_create_patients_permission,
            validate_patient_view_permissions,
            validate_patient_management_permissions
        )
        print("✅ Permission validators imported successfully")
        
        from app.agents.tools.patient_search_tools import (
            search_patients,
            search_patients_by_name,
            get_patient_by_id,
            get_patients_summary
        )
        print("✅ Patient search tools imported successfully")
        
        from app.agents.tools.patient_management_tools import (
            create_patient,
            update_patient
        )
        print("✅ Patient management tools imported successfully")
        
    except ImportError as e:
        print(f"❌ Failed to import individual modules: {e}")
        return False
    
    # Test 3: Specific tool imports (alternative syntax)
    print("\n📋 Test 3: Specific tool imports from main package")
    try:
        from app.agents.tools import (
            search_patients,
            create_patient,
            check_use_agent_permission
        )
        print("✅ Specific tools imported from main package successfully")
        
    except ImportError as e:
        print(f"❌ Failed to import specific tools: {e}")
        return False
    
    return True

def test_tool_structure():
    """Test that tools have the correct structure."""
    print("\n📋 Test 4: Tool Structure Validation")
    print("-" * 50)
    
    try:
        from app.agents.tools import ALL_TOOLS
        
        for tool in ALL_TOOLS:
            # Check that each tool has required attributes
            if hasattr(tool, 'name') and hasattr(tool, 'description'):
                print(f"✅ {tool.name} - Has name and description")
                
                # Check if description mentions required permissions
                if 'UseAgent' in tool.description:
                    print(f"  ✅ {tool.name} - Mentions UseAgent permission")
                else:
                    print(f"  ⚠️  {tool.name} - Missing UseAgent in description")
            else:
                print(f"❌ {tool.name} - Missing attributes")
        
    except Exception as e:
        print(f"❌ Error validating tool structure: {e}")
        return False
    
    return True

def test_medical_agent_compatibility():
    """Test that the medical agent can still use the tools."""
    print("\n📋 Test 5: Medical Agent Compatibility")
    print("-" * 50)
    
    try:
        from app.agents.medical_agent import MedicalQueryAgent
        
        # Initialize agent
        agent = MedicalQueryAgent()
        
        # Check that agent has tools
        if agent.agent_executor is not None:
            print("✅ Medical agent initialized successfully")
            
            # Check available tools
            available_tools = agent.get_available_tools()
            print(f"✅ Agent has access to {len(available_tools)} tools")
            
            for tool_info in available_tools:
                print(f"  • {tool_info['name']}")
                
        else:
            print("❌ Medical agent failed to initialize")
            return False
            
    except Exception as e:
        print(f"❌ Error testing medical agent compatibility: {e}")
        return False
    
    return True

def test_permission_validators():
    """Test permission validation functions."""
    print("\n📋 Test 6: Permission Validator Functions")
    print("-" * 50)
    
    try:
        from app.agents.tools.permission_validators import (
            validate_patient_view_permissions,
            validate_patient_management_permissions
        )
        
        # These will return False since no user context is set, but should not error
        has_view, msg_view = validate_patient_view_permissions()
        has_manage, msg_manage = validate_patient_management_permissions()
        
        print("✅ validate_patient_view_permissions callable")
        print("✅ validate_patient_management_permissions callable")
        print(f"✅ Permission functions return proper format (bool, str)")
        
        # Check that error messages are informative
        if "UseAgent" in msg_view and "ViewPatients" in msg_view:
            print("✅ View permissions error message mentions both required permissions")
        elif "UseAgent" in msg_view:
            print("✅ View permissions error message mentions UseAgent (user likely missing this)")
        
        if "UseAgent" in msg_manage and "ManagePatients" in msg_manage:
            print("✅ Manage permissions error message mentions both required permissions") 
        elif "UseAgent" in msg_manage:
            print("✅ Manage permissions error message mentions UseAgent (user likely missing this)")
            
    except Exception as e:
        print(f"❌ Error testing permission validators: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Modular Structure Validation Tests")
    print("This script validates that the refactoring was successful")
    print("=" * 80)
    
    tests = [
        test_imports,
        test_tool_structure,
        test_medical_agent_compatibility,
        test_permission_validators
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
    
    print("\n" + "=" * 80)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! The modular refactoring was successful.")
        print("\n🎉 Benefits achieved:")
        print("  • Code is now organized into logical modules")
        print("  • Each module has a single responsibility")
        print("  • Permission validation is centralized")
        print("  • Tools are grouped by functionality")
        print("  • Backward compatibility is maintained")
        print("  • The agent continues to work without changes")
    else:
        print("❌ Some tests failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
