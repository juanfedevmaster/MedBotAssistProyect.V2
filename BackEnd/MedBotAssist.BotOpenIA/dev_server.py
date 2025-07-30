"""
Development server script for Windows
Solves multiprocessing issues with uvicorn --reload on Windows
"""
import uvicorn
import sys
import os

if __name__ == "__main__":
    # Add the project root to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run uvicorn with Windows-compatible settings
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["*.pyc", "__pycache__"],
        log_level="info"
    )
