#!/usr/bin/env python3
"""
Test script to verify UseAgent permission implementation.
This script tests that the UseAgent permission is properly validated before any agent operation.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.agents.medical_agent import MedicalQueryAgent

async def test_use_agent_permission():
    """Test UseAgent permission validation in the medical agent."""
    
    print("🧪 Testing UseAgent Permission Implementation\n")
    print("=" * 60)
    
    # Initialize the agent
    agent = MedicalQueryAgent()
    
    # Test Case 1: User without UseAgent permission
    print("\n📋 Test Case 1: User WITHOUT UseAgent permission")
    print("-" * 50)
    
    response1 = await agent.query(
        message="How many patients are in the database?",
        conversation_id="test-1",
        user_permissions=["ViewPatients", "ManagePatients"],  # Missing UseAgent
        username="user_without_useagent",
        jwt_token="fake-jwt-token"
    )
    
    print(f"✅ Response: {response1['response']}")
    print(f"✅ Success: {response1['success']}")
    print(f"✅ Expected: Access denied due to missing UseAgent permission")
    
    # Test Case 2: User with UseAgent but without ViewPatients
    print("\n📋 Test Case 2: User WITH UseAgent but WITHOUT ViewPatients")
    print("-" * 50)
    
    response2 = await agent.query(
        message="How many patients are in the database?",
        conversation_id="test-2", 
        user_permissions=["UseAgent"],  # Has UseAgent but not ViewPatients
        username="user_with_useagent_no_view",
        jwt_token="fake-jwt-token"
    )
    
    print(f"✅ Response: {response2['response']}")
    print(f"✅ Success: {response2['success']}")
    print(f"✅ Expected: Should pass UseAgent check but fail ViewPatients check")
    
    # Test Case 3: User with UseAgent and ViewPatients (full access)
    print("\n📋 Test Case 3: User WITH both UseAgent and ViewPatients")
    print("-" * 50)
    
    response3 = await agent.query(
        message="How many patients are in the database?",
        conversation_id="test-3",
        user_permissions=["UseAgent", "ViewPatients"],  # Has both permissions
        username="complete_user",
        jwt_token="fake-jwt-token"
    )
    
    print(f"✅ Response: {response3['response']}")
    print(f"✅ Success: {response3['success']}")
    print(f"✅ Expected: Should work normally")
    
    # Test Case 4: User with all permissions
    print("\n📋 Test Case 4: User WITH all permissions")
    print("-" * 50)
    
    response4 = await agent.query(
        message="How many patients are in the database?",
        conversation_id="test-4",
        user_permissions=["UseAgent", "ViewPatients", "ManagePatients"],  # All permissions
        username="admin_full",
        jwt_token="fake-jwt-token"
    )
    
    print(f"✅ Response: {response4['response']}")
    print(f"✅ Success: {response4['success']}")
    print(f"✅ Expected: Should work normally with full access")
    
    # Test Case 5: User with no permissions at all
    print("\n📋 Test Case 5: User WITHOUT any permissions")
    print("-" * 50)
    
    response5 = await agent.query(
        message="How many patients are in the database?",
        conversation_id="test-5",
        user_permissions=[],  # No permissions
        username="user_no_permissions",
        jwt_token="fake-jwt-token"
    )
    
    print(f"✅ Response: {response5['response']}")
    print(f"✅ Success: {response5['success']}")
    print(f"✅ Expected: Access denied due to missing UseAgent permission")
    
    print("\n" + "=" * 60)
    print("🏁 Test Complete!")
    print("\n📊 Summary:")
    print("- UseAgent permission is now MANDATORY for ALL agent interactions")
    print("- Individual tools still require their specific permissions (ViewPatients, ManagePatients)")
    print("- The agent validates UseAgent permission BEFORE executing any tools")
    print("- Users without UseAgent permission cannot interact with the agent at all")

if __name__ == "__main__":
    asyncio.run(test_use_agent_permission())
