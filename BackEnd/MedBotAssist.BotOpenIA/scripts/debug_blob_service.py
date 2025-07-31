#!/usr/bin/env python3
"""
Test script to debug blob service URL construction
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.blob_service import BlobService
import logging

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# The real SAS token from the user
SAS_TOKEN = "sv=2025-07-05&se=2025-07-31T18%3A33%3A30Z&sr=c&sp=rcwdl&sig=P05relRydQUZkDSI6hmXi4UzpInlDTUEFOVmpbNPBp0%3D"

async def test_blob_service():
    """Test the blob service directly"""
    print("🧪 BLOB SERVICE DIRECT TEST")
    print("=" * 50)
    
    blob_service = BlobService()
    
    # Test URL construction
    print(f"Base URL: {blob_service.base_url}")
    print(f"Container: {blob_service.container_name}")
    
    # Test _build_blob_url method
    test_url = blob_service._build_blob_url(sas_token=SAS_TOKEN)
    print(f"Built URL: {test_url}")
    
    # Compare with working URL
    working_url = "https://strmedbotassist.blob.core.windows.net/instructions-files?sv=2025-07-05&se=2025-07-31T18%3A33%3A30Z&sr=c&sp=rcwdl&sig=P05relRydQUZkDSI6hmXi4UzpInlDTUEFOVmpbNPBp0%3D&restype=container&comp=list"
    print(f"Working URL: {working_url}")
    
    # Try to list blobs
    print(f"\nTesting list_blobs method:")
    try:
        blobs = await blob_service.list_blobs(SAS_TOKEN)
        print(f"✅ Successfully listed {len(blobs)} blobs")
        for blob in blobs:
            print(f"   - {blob.get('name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")
        
    print("\nDone!")

if __name__ == "__main__":
    asyncio.run(test_blob_service())
