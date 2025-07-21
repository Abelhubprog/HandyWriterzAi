#!/usr/bin/env python3
"""
Basic startup test for HandyWriterz backend
Tests if all imports work and the server can initialize
"""

import sys
import os
import traceback
from pathlib import Path

# Add the src directory to Python path
backend_dir = Path(__file__).parent
src_dir = backend_dir / "src"
sys.path.insert(0, str(src_dir))

def test_basic_imports():
    """Test basic imports to identify what's broken."""
    print("🧪 Testing basic imports...")
    
    try:
        print("  ✓ Testing FastAPI...")
        import fastapi
        print("  ✓ FastAPI OK")
        
        print("  ✓ Testing LangGraph...")
        import langgraph
        print("  ✓ LangGraph OK")
        
        print("  ✓ Testing environment loading...")
        from dotenv import load_dotenv
        load_dotenv()
        print("  ✓ Environment loading OK")
        
        print("  ✓ Testing agent base...")
        from src.agent.base import UserParams, BaseNode
        print("  ✓ Agent base OK")
        
        print("  ✓ Testing HandyWriterz state...")
        from src.agent.handywriterz_state import HandyWriterzState
        print("  ✓ HandyWriterz state OK")
        
        print("  ✓ Testing HandyWriterz graph...")
        from src.agent.handywriterz_graph import handywriterz_graph
        print("  ✓ HandyWriterz graph OK")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        print(f"  📍 Traceback:")
        traceback.print_exc()
        return False

def test_simple_server_startup():
    """Test if the simple server can start."""
    print("\n🚀 Testing simple server startup...")
    
    try:
        # Test the simple server
        print("  ✓ Testing handywriterz_server.py...")
        
        # Import the simple server app
        sys.path.insert(0, str(backend_dir))
        from handywriterz_server import app
        
        print("  ✓ Simple server app created successfully")
        
        # Test a basic endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        response = client.get("/health")
        print(f"  ✓ Health check response: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Simple server startup failed: {e}")
        traceback.print_exc()
        return False

def test_advanced_server_startup():
    """Test if the advanced server can start."""
    print("\n🚀 Testing advanced server startup...")
    
    try:
        # Test the advanced server
        print("  ✓ Testing main.py...")
        
        # This will likely fail, but let's see how far we get
        from src.main import app
        
        print("  ✓ Advanced server app created successfully")
        return True
        
    except Exception as e:
        print(f"  ❌ Advanced server startup failed: {e}")
        print("  📝 This is expected - advanced server has more dependencies")
        return False

def main():
    """Run all tests."""
    print("🎯 HandyWriterz Backend Startup Test")
    print("=" * 50)
    
    # Test imports first
    imports_ok = test_basic_imports()
    
    # Test simple server
    simple_ok = test_simple_server_startup()
    
    # Test advanced server
    advanced_ok = test_advanced_server_startup()
    
    print("\n📊 Test Results:")
    print(f"  Basic Imports: {'✅ PASS' if imports_ok else '❌ FAIL'}")
    print(f"  Simple Server: {'✅ PASS' if simple_ok else '❌ FAIL'}")
    print(f"  Advanced Server: {'✅ PASS' if advanced_ok else '❌ FAIL'}")
    
    if simple_ok:
        print("\n🎉 GOOD NEWS: Simple server is working!")
        print("   You can start the demo with: python handywriterz_server.py")
    
    if not imports_ok:
        print("\n⚠️  CRITICAL: Fix imports first with: pip install -r requirements.txt")
    
    return imports_ok and simple_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)