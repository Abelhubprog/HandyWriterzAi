#!/usr/bin/env python3
"""
Minimal Installation Script for Python 3.14
Installs only essential packages and sets up the database.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and handle errors."""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"   {e.stderr.strip()}")
        return False


def install_essential_packages():
    """Install only essential packages that work with Python 3.14."""
    essential_packages = [
        "fastapi>=0.110.0",
        "uvicorn[standard]>=0.27.0",
        "python-dotenv>=1.0.1",
        "aiofiles>=23.2.1",
        "aiohttp>=3.9.3",
        "pydantic>=2.6.0",
        "python-multipart>=0.0.9"
    ]
    
    print("📦 Installing essential packages for Python 3.14...")
    
    for package in essential_packages:
        success = run_command(
            f"{sys.executable} -m pip install '{package}' --no-deps --force-reinstall",
            f"Installing {package}"
        )
        if not success:
            print(f"⚠️  Warning: Failed to install {package}")
    
    return True


def install_database_packages():
    """Install database packages with fallbacks."""
    print("🗄️  Installing database packages...")
    
    # Try modern packages first, fallback to older ones
    database_packages = [
        ("aiosqlite>=0.19.0", "SQLite async support"),
    ]
    
    for package, description in database_packages:
        run_command(
            f"{sys.executable} -m pip install '{package}'",
            f"Installing {description}"
        )


def create_minimal_database():
    """Create database using Python's built-in sqlite3."""
    print("🗄️  Creating minimal database...")
    
    try:
        # Import and run the database creation
        sys.path.insert(0, str(Path(__file__).parent))
        from init_database import create_sqlite_database, create_env_template
        
        success = create_sqlite_database()
        if success:
            create_env_template()
            return True
        return False
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False


def create_minimal_main():
    """Create a minimal main.py that works without all dependencies."""
    main_content = '''#!/usr/bin/env python3
"""
Minimal HandyWriterz Backend for Python 3.14
Basic FastAPI server with database setup.
"""

import os
import sqlite3
import uvicorn
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Initialize FastAPI app
app = FastAPI(
    title="HandyWriterz Backend - Minimal",
    description="Minimal backend for Python 3.14 compatibility",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = Path(__file__).parent.parent / "handywriterz.db"


class ModelConfig(BaseModel):
    """Model configuration."""
    stage: str
    model_name: str


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "HandyWriterz Backend - Minimal Mode", "status": "running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected" if DB_PATH.exists() else "missing"
    }


@app.get("/api/models")
async def get_models():
    """Get model configuration."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT stage, model_name FROM model_map WHERE is_active = 1")
        models = [{"stage": row[0], "model_name": row[1]} for row in cursor.fetchall()]
        
        conn.close()
        
        return {"models": models}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.post("/api/models")
async def update_model(config: ModelConfig):
    """Update model configuration."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Update or insert model configuration
        cursor.execute("""
            INSERT OR REPLACE INTO model_map (stage, model_name, is_active)
            VALUES (?, ?, 1)
        """, (config.stage, config.model_name))
        
        conn.commit()
        conn.close()
        
        return {"message": f"Model {config.stage} updated to {config.model_name}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@app.get("/api/status")
async def system_status():
    """System status endpoint."""
    try:
        # Check database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM model_map")
        model_count = cursor.fetchone()[0]
        conn.close()
        
        return {
            "status": "operational",
            "version": "1.0.0-minimal",
            "features": {
                "database": True,
                "model_config": True,
                "full_ai_stack": False
            },
            "model_count": model_count,
            "message": "Minimal mode - Database operations available"
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e),
            "features": {
                "database": False,
                "model_config": False,
                "full_ai_stack": False
            }
        }


if __name__ == "__main__":
    # Check if database exists
    if not DB_PATH.exists():
        print("❌ Database not found. Run: python scripts/init_database.py")
        exit(1)
    
    print("🚀 Starting HandyWriterz Backend - Minimal Mode")
    print(f"📄 Database: {DB_PATH}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''
    
    main_path = Path(__file__).parent.parent / "src" / "main_minimal.py"
    with open(main_path, "w") as f:
        f.write(main_content)
    
    print(f"📝 Created minimal main.py: {main_path}")


def main():
    """Main installation function."""
    print("🚀 HandyWriterz Minimal Installation for Python 3.14")
    print("=" * 60)
    
    # Step 1: Install essential packages
    install_essential_packages()
    
    # Step 2: Install database packages
    install_database_packages()
    
    # Step 3: Create database
    db_success = create_minimal_database()
    
    # Step 4: Create minimal main
    create_minimal_main()
    
    if db_success:
        print("\n✅ Minimal installation complete!")
        print("\n📋 What's available:")
        print("✅ Database with model configuration")
        print("✅ Basic FastAPI server")
        print("✅ Model configuration API")
        print("✅ Health check endpoints")
        
        print("\n🚀 To start the server:")
        print("   cd backend/src")
        print("   python main_minimal.py")
        
        print("\n🌐 Then visit:")
        print("   http://localhost:8000/docs - API documentation")
        print("   http://localhost:8000/api/models - Model configuration")
        
        print("\n⚠️  Note: This is minimal mode.")
        print("   Full AI features require additional package installation.")
        
    else:
        print("\n❌ Installation failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()