from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import agent
import uvicorn

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
    allow_origins=["*"],  # Permitir todos los orígenes para Azure
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers - agente principal que se adapta al entorno
app.include_router(
    agent.router,
    prefix="/api/v1/agent",
    tags=["agent"]
)

@app.get("/")
async def root():
    return {"message": "MedBot Assistant API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is operational"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
