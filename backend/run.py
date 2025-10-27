import uvicorn
import sys
import os
from pathlib import Path

# Ensure we're using the venv Python
venv_python = Path(__file__).parent / "venv" / "Scripts" / "python.exe"
if venv_python.exists() and str(venv_python) != sys.executable:
    print(f"Warning: Not running from venv. Current: {sys.executable}")
    print(f"Expected: {venv_python}")

from app.core.config import settings

if __name__ == "__main__":
    print(f"Starting backend with Python: {sys.executable}")
    print(f"Debug mode: {settings.DEBUG}")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid Python path issues
        log_level="info"
    )
