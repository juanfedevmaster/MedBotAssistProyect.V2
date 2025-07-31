#!/usr/bin/env python3
"""
Script to test Azure Blob Storage connectivity and diagnose issues.

This script will help identify if the problem is:
1. Container doesn't exist
2. SAS token permissions
3. URL construction issues
4. Network connectivity
"""

import asyncio
import httpx
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.blob_service import BlobService
from app.core.config import settings
import logging

# Configure logging to see detailed information
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test SAS token (from generate_test_jwt.py)
TEST_SAS_TOKEN = "sp=r&st=2024-01-01T00:00:00Z&se=2024-12-31T23:59:59Z&sv=2023-01-03&sr=c&sig=EXAMPLE_SAS_TOKEN"

async def test_blob_storage_connectivity():
    """Test basic connectivity to Azure Blob Storage."""
    print("🧪 BLOB STORAGE CONNECTIVITY TEST")
    print("=" * 50)
    
    # Initialize blob service
    blob_service = BlobService()
    
    # Show configuration
    config = blob_service.get_container_info()
    print(f"📋 Configuration:")
    print(f"   - Base URL: {config['base_url']}")
    print(f"   - Container: {config['container_name']}")
    print(f"   - Timeout: {config['timeout_seconds']}s")
    
    # Test 1: Check if we can build URLs correctly
    print(f"\n🔧 Test 1: URL Construction")
    test_url = blob_service._build_blob_url(sas_token=TEST_SAS_TOKEN)
    print(f"   Container URL: {test_url}")
    
    test_blob_url = blob_service._build_blob_url("test.pdf", TEST_SAS_TOKEN)
    print(f"   Blob URL: {test_blob_url}")
    
    # Test 2: Try to list blobs
    print(f"\n📂 Test 2: List Blobs")
    try:
        blobs = await blob_service.list_blobs(TEST_SAS_TOKEN)
        print(f"   ✅ Successfully listed {len(blobs)} blobs")
        for blob in blobs[:3]:  # Show first 3 blobs
            print(f"      - {blob.get('name', 'Unknown')} ({blob.get('size', 0)} bytes)")
    except Exception as e:
        print(f"   ❌ Error listing blobs: {e}")
        return False
    
    # Test 3: Try a direct HTTP request to see raw response
    print(f"\n🌐 Test 3: Direct HTTP Request")
    try:
        url = blob_service._build_blob_url(sas_token=TEST_SAS_TOKEN)
        params = {
            "restype": "container",
            "comp": "list"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=params)
            print(f"   Status Code: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('content-type', 'N/A')}")
            print(f"   Content-Length: {response.headers.get('content-length', 'N/A')}")
            
            if response.status_code != 200:
                print(f"   ❌ Response Body: {response.text[:500]}...")
            else:
                print(f"   ✅ Response Body Preview: {response.text[:200]}...")
                
    except Exception as e:
        print(f"   ❌ Direct HTTP request failed: {e}")
        return False
    
    return True

async def test_container_existence():
    """Test if the specific container exists."""
    print(f"\n🗂️  Test 4: Container Existence Check")
    
    base_url = settings.BLOB_STORAGE_BASE_URL
    container_name = settings.BLOB_CONTAINER_NAME
    
    # Try to access container metadata
    try:
        url = f"{base_url}/{container_name}?{TEST_SAS_TOKEN}&restype=container"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.head(url)
            
            if response.status_code == 200:
                print(f"   ✅ Container '{container_name}' exists and is accessible")
                return True
            elif response.status_code == 404:
                print(f"   ❌ Container '{container_name}' does not exist")
                return False
            elif response.status_code == 403:
                print(f"   ❌ Access denied to container '{container_name}' - check SAS token permissions")
                return False
            else:
                print(f"   ⚠️  Unexpected response: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error checking container: {e}")
        return False

async def suggest_solutions():
    """Provide suggestions for common issues."""
    print(f"\n💡 POSSIBLE SOLUTIONS:")
    print("=" * 50)
    print("1. 🗂️  Container Missing:")
    print("   - Create the 'instructions-files' container in Azure Portal")
    print("   - Ensure the container is set to 'Blob' or 'Container' access level")
    
    print("\n2. 🔑 SAS Token Issues:")
    print("   - Verify SAS token has 'Read' and 'List' permissions")
    print("   - Check SAS token hasn't expired")
    print("   - Ensure SAS token is for the correct container")
    
    print("\n3. 🌐 URL/Configuration Issues:")
    print("   - Verify BLOB_STORAGE_BASE_URL in config")
    print("   - Check BLOB_CONTAINER_NAME spelling")
    print("   - Ensure network connectivity to Azure")
    
    print("\n4. 🔧 Development Setup:")
    print("   - For development, you can skip blob storage by setting up local file system")
    print("   - Use Azure Storage Emulator for local testing")

async def main():
    """Run all blob storage tests."""
    print("🧪 AZURE BLOB STORAGE DIAGNOSTIC TOOL")
    print("=" * 60)
    print(f"Date: {asyncio.get_event_loop().time()}")
    print(f"Testing connectivity to: {settings.BLOB_STORAGE_BASE_URL}")
    print(f"Container: {settings.BLOB_CONTAINER_NAME}")
    
    try:
        # Run tests
        connectivity_ok = await test_blob_storage_connectivity()
        container_exists = await test_container_existence()
        
        # Summary
        print(f"\n📊 TEST SUMMARY:")
        print("=" * 30)
        print(f"Connectivity: {'✅ PASS' if connectivity_ok else '❌ FAIL'}")
        print(f"Container Exists: {'✅ PASS' if container_exists else '❌ FAIL'}")
        
        if not connectivity_ok or not container_exists:
            await suggest_solutions()
        else:
            print("🎉 All tests passed! Blob storage should be working correctly.")
            
    except Exception as e:
        print(f"❌ Unexpected error during testing: {e}")
        await suggest_solutions()

if __name__ == "__main__":
    asyncio.run(main())
