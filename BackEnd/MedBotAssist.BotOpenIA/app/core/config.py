from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MedBot Assistant API"
    VERSION: str = "1.0.0"
    
    # CORS Configuration
    ALLOWED_HOSTS: List[str] = ["*"]  # Configure according to your needs
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # SQL Server Database Configuration
    DB_SERVER: str = "medbotserver.database.windows.net"
    DB_DATABASE: str = "MedBotAssistDB"
    DB_USER: str = "medicaluser"
    DB_PASSWORD: str = "Admin123!"
    DB_DRIVER: str = "ODBC Driver 17 for SQL Server"  # Use version 17 which is more widely available
    
    # JWT Configuration
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "MedBotAssist")
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "MedBotAssistUsers")
    JWT_EXPIRATION_MINUTES: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    
    # External Backend API Configuration
    EXTERNAL_BACKEND_API_URL: str = os.getenv("EXTERNAL_BACKEND_API_URL", "http://localhost:5098/api/")
    
    # Azure Blob Storage Configuration
    BLOB_STORAGE_BASE_URL: str = os.getenv("BLOB_STORAGE_BASE_URL", "https://strmedbotassist.blob.core.windows.net")
    BLOB_CONTAINER_NAME: str = os.getenv("BLOB_CONTAINER_NAME", "instructions-files")
    
    # Vectorization Configuration
    VECTOR_DB_PATH: str = os.getenv("VECTOR_DB_PATH", "./chroma_db")
    DEFAULT_COLLECTION_NAME: str = os.getenv("DEFAULT_COLLECTION_NAME", "medical_documents")
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "200"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "120"))
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()
