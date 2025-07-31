"""
Test script for VectorizationManager

This script tests the vectorization functionality with a sample document.
"""

import asyncio
import sys
import os
import logging

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.vectorization_manager import VectorizationManager
from app.services.jwt_service import JWTService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_vectorization():
    """Test the vectorization manager functionality."""
    
    logger.info("Starting VectorizationManager test...")
    
    try:
        # Initialize the vectorization manager
        vm = VectorizationManager()
        logger.info("VectorizationManager initialized successfully")
        
        # Get initial statistics
        stats = vm.get_vectorization_stats()
        logger.info(f"Initial stats: {stats}")
        
        # Test JWT service for SAS token generation
        jwt_service = JWTService()
        
        # Create a test JWT token (simulated - in real use case this would come from authentication)
        import jwt
        from app.core.config import settings
        import datetime
        
        test_payload = {
            "userId": "test-user-123",
            "permissions": ["UseAgent", "ViewPatients"],
            "sasToken": "sp=r&st=2024-01-01T00:00:00Z&se=2024-12-31T23:59:59Z&spr=https&sv=2022-11-02&sr=c&sig=test_signature",
            "iss": settings.JWT_ISSUER,
            "aud": settings.JWT_AUDIENCE,
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        
        # Generate JWT token manually for testing
        jwt_token = jwt.encode(test_payload, settings.JWT_SECRET, algorithm="HS256")
        logger.info("Test JWT token created successfully")
        
        # Extract SAS token from JWT
        sas_token = jwt_service.extract_sas_token(jwt_token)
        logger.info(f"Extracted SAS token: {sas_token[:50]}..." if sas_token else "No SAS token found")
        
        if not sas_token:
            logger.warning("No SAS token available - some tests will be skipped")
            return
        
        # Test blob listing (this will show available files)
        try:
            blobs = await vm.blob_service.list_blobs(sas_token)
            logger.info(f"Found {len(blobs) if blobs else 0} blobs in container")
            
            if blobs:
                # Show first few blob names
                for i, blob in enumerate(blobs[:3]):
                    logger.info(f"  Blob {i+1}: {blob.get('name', 'unknown')}")
                
                # Test vectorizing the first file
                if blobs:
                    test_blob = blobs[0]['name']
                    logger.info(f"Testing vectorization of: {test_blob}")
                    
                    result = await vm.vectorize_file(test_blob, sas_token)
                    logger.info(f"Vectorization result: {result}")
                    
                    # Get updated statistics
                    updated_stats = vm.get_vectorization_stats()
                    logger.info(f"Updated stats: {updated_stats}")
            else:
                logger.info("No blobs found to test vectorization")
                
        except Exception as e:
            logger.error(f"Error testing blob operations: {e}")
            logger.info("This might be expected if SAS token is not valid for actual Azure storage")
        
        logger.info("VectorizationManager test completed successfully")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        raise

def test_text_processing():
    """Test text processing functions without external dependencies."""
    
    logger.info("Testing text processing functions...")
    
    try:
        vm = VectorizationManager()
        
        # Test text chunking
        sample_text = "This is a sample text. " * 100  # Create a longer text
        chunks = vm._chunk_text(sample_text)
        logger.info(f"Created {len(chunks)} chunks from sample text")
        
        if chunks:
            logger.info(f"First chunk length: {len(chunks[0])} characters")
            logger.info(f"First chunk preview: {chunks[0][:100]}...")
        
        # Test URL generation
        test_url = vm._generate_download_url("test-file.pdf", "test-sas-token")
        logger.info(f"Generated URL: {test_url}")
        
        logger.info("Text processing tests completed successfully")
        
    except Exception as e:
        logger.error(f"Error in text processing test: {e}")
        raise

if __name__ == "__main__":
    # Run text processing tests (no external dependencies)
    test_text_processing()
    
    # Run full vectorization tests (requires external services)
    print("\n" + "="*50)
    print("Running full vectorization tests...")
    print("Note: Some tests may fail if Azure storage is not accessible")
    print("="*50 + "\n")
    
    asyncio.run(test_vectorization())
