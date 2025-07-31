#!/usr/bin/env python3
"""
Test script for Blob Storage Service
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.blob_service import BlobService
from app.services.jwt_service import JWTService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_blob_service():
    """Test the blob service functionality."""
    
    print("🧪 Testing Blob Service")
    print("=" * 50)
    
    # Initialize services
    blob_service = BlobService()
    jwt_service = JWTService()
    
    # Test JWT with SAS token (you need to provide a real SAS token)
    test_sas_token = "sp=rl&st=2024-01-01T00:00:00Z&se=2024-12-31T23:59:59Z&spr=https&sv=2023-01-03&sr=c&sig=REPLACE_WITH_REAL_SAS_SIGNATURE"
    
    print(f"📋 Service Info:")
    info = blob_service.get_container_info()
    for key, value in info.items():
        print(f"  {key}: {value}")
    
    print(f"\n🔗 Testing with SAS Token: {test_sas_token[:50]}...")
    
    try:
        # Test 1: List blobs
        print(f"\n1️⃣  Testing: List blobs")
        blobs = await blob_service.list_blobs(test_sas_token)
        print(f"✅ Found {len(blobs)} blobs")
        
        if blobs:
            print("📂 Files found:")
            for i, blob in enumerate(blobs[:5], 1):  # Show first 5
                name = blob.get('name', 'Unknown')
                size = blob.get('size', 0)
                content_type = blob.get('content_type', 'Unknown')
                print(f"  {i}. {name} ({size} bytes, {content_type})")
            
            if len(blobs) > 5:
                print(f"  ... and {len(blobs) - 5} more files")
            
            # Test 2: Get metadata for first blob
            first_blob_name = blobs[0].get('name')
            if first_blob_name:
                print(f"\n2️⃣  Testing: Get metadata for '{first_blob_name}'")
                metadata = await blob_service.get_blob_metadata(first_blob_name, test_sas_token)
                print("✅ Metadata retrieved:")
                for key, value in metadata.items():
                    print(f"  {key}: {value}")
                
                # Test 3: Check if blob exists
                print(f"\n3️⃣  Testing: Check if blob exists")
                exists = await blob_service.blob_exists(first_blob_name, test_sas_token)
                print(f"✅ Blob exists: {exists}")
                
                # Test 4: Download blob (first few bytes only for testing)
                print(f"\n4️⃣  Testing: Download blob (first 1024 bytes)")
                content, download_metadata = await blob_service.download_blob(first_blob_name, test_sas_token)
                print(f"✅ Downloaded {len(content)} bytes")
                print(f"📋 Download metadata:")
                for key, value in download_metadata.items():
                    print(f"  {key}: {value}")
                
                # Show first few bytes as hex
                if content:
                    preview = content[:50]
                    hex_preview = ' '.join(f'{b:02x}' for b in preview)
                    print(f"🔍 Content preview (hex): {hex_preview}...")
        else:
            print("📭 No blobs found in container")
        
        # Test 5: Test non-existent blob
        print(f"\n5️⃣  Testing: Check non-existent blob")
        exists = await blob_service.blob_exists("non-existent-file.txt", test_sas_token)
        print(f"✅ Non-existent blob exists: {exists}")
        
        print(f"\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Blob service test error: {e}", exc_info=True)

def main():
    """Main function to run the tests."""
    
    print("🗂️  MedBot Assistant - Blob Service Test")
    print("=" * 60)
    
    print("⚠️  IMPORTANT:")
    print("This test requires a valid SAS token. Please:")
    print("1. Get a SAS token from Azure Portal for 'instructions-files' container")
    print("2. Update the 'test_sas_token' variable in this script")
    print("3. Ensure the SAS token has 'Read' and 'List' permissions")
    print()
    
    response = input("Do you want to continue with the test? (y/N): ")
    if response.lower() != 'y':
        print("Test cancelled.")
        return
    
    # Run the async test
    try:
        asyncio.run(test_blob_service())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    main()
