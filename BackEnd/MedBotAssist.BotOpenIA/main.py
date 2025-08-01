from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import agent, blob, vectorization
import uvicorn
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI instance
app = FastAPI(
    title="MedBot Assistant API",
    description="API para asistente médico con capacidades de vectorización y agentes IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Azure
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - principal agent that adapts to the environment
app.include_router(
    agent.router,
    prefix="/api/v1/agent",
    tags=["agent"]
)

# Include blob storage routes
app.include_router(
    blob.router,
    prefix="/api/v1/blob",
    tags=["blob-storage"]
)

# Include vectorization routes
app.include_router(
    vectorization.router,
    prefix="/api/v1/vectorization",
    tags=["vectorization"]
)

@app.get("/")
async def root():
    return {"message": "MedBot Assistant API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is operational"}

@app.on_event("startup")
async def startup_event():
    """
    Event handler that runs when the FastAPI application starts.
    Performs auto-vectorization if the vector database is empty.
    """
    logger.info("FastAPI application starting up...")
    
    try:
        # Import here to avoid circular imports
        from app.services.vectorization_manager import vectorization_manager
        
        # Check if auto-vectorization should run
        result = await vectorization_manager.auto_vectorize_on_startup()
        
        if result["status"] == "completed":
            files_processed = result.get('files_processed', 0)
            total_chunks = result.get('total_chunks', 0)
            logger.info(f"✅ Auto-vectorization completed: {files_processed} files processed, {total_chunks} chunks created")
        elif result["status"] == "skipped":
            logger.info(f"⏭️ Auto-vectorization skipped: {result['message']}")
        elif result["status"] == "disabled":
            logger.info("🔒 Auto-vectorization is disabled in configuration")
        else:
            logger.warning(f"⚠️ Auto-vectorization issue: {result['message']}")
            
    except Exception as e:
        logger.error(f"❌ Error during startup auto-vectorization: {e}")
        # Don't fail the startup, just log the error
    
    logger.info("FastAPI application startup completed")

if __name__ == "__main__":
    # For development - includes hot reload and better logging
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        reload=True,
        log_level="info"
    )
