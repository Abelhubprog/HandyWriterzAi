#!/usr/bin/env python3
"""
Quick start script for the real HandyWriterz system
"""
import os
import sys
import uvicorn

# Add src to path
sys.path.insert(0, 'src')

print("🚀 Starting HandyWriterz Real Multi-Agent System...")
print("🔍 This will connect to your complete LangGraph pipeline")
print("⚡ NO MOCKING - All responses from real agents")

# Import the real system directly
from src.main import app

if __name__ == "__main__":
    print("✅ Real system loaded successfully!")
    print("📡 Starting server with all 30+ agents...")
    
    uvicorn.run(
        "quick_start:app",
        host="0.0.0.0", 
        port=8000,
        reload=False,  # Disable reload for faster startup
        log_level="info"
    )