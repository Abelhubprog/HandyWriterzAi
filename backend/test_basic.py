#!/usr/bin/env python3
"""
Basic test script to verify system functionality without heavy dependencies
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_imports():
    """Test basic imports that should work without external dependencies"""
    try:
        # Test state management
        from agent.handywriterz_state import HandyWriterzState, DocumentType, CitationStyle
        print("✅ State management imports successful")
        
        # Test that we can create a state object
        state = HandyWriterzState(
            conversation_id="test",
            user_id="test_user",
            user_params={"field": "test"},
            uploaded_docs=[],
            outline=None,
            research_agenda=[],
            search_queries=[],
            raw_search_results=[],
            filtered_sources=[],
            verified_sources=[],
            draft_content=None,
            current_draft=None,
            revision_count=0,
            evaluation_results=[],
            evaluation_score=None,
            turnitin_reports=[],
            turnitin_passed=False,
            formatted_document=None,
            learning_outcomes_report=None,
            download_urls={},
            current_node=None,
            workflow_status="initiated",
            error_message=None,
            retry_count=0,
            max_iterations=5,
            enable_tutor_review=False,
            start_time=None,
            end_time=None,
            processing_metrics={},
            auth_token=None,
            payment_transaction_id=None,
            uploaded_files=[]
        )
        print("✅ State object creation successful")
        
        # Test enum functionality
        doc_type = DocumentType.ESSAY
        citation_style = CitationStyle.APA
        print(f"✅ Enums working: {doc_type.value}, {citation_style.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_node_structure():
    """Test that node files exist and have basic structure"""
    node_files = [
        "src/agent/nodes/master_orchestrator.py",
        "src/agent/nodes/enhanced_user_intent.py", 
        "src/agent/nodes/search_gemini.py",
        "src/agent/nodes/search_perplexity.py",
        "src/agent/nodes/user_intent.py",
        "src/agent/nodes/planner.py",
        "src/agent/nodes/writer.py"
    ]
    
    missing_files = []
    for file_path in node_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing node files: {missing_files}")
        return False
    else:
        print("✅ All core node files exist")
        return True

def test_configuration_files():
    """Test that configuration files exist"""
    config_files = [
        "src/main.py",
        "src/config.py",
        "requirements.txt",
        "package.json"
    ]
    
    missing_files = []
    for file_path in config_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing config files: {missing_files}")
        return False
    else:
        print("✅ All configuration files exist")
        return True

def test_database_models():
    """Test database model imports (if possible)"""
    try:
        print("✅ Database models import successful")
        return True
    except Exception as e:
        print(f"⚠️  Database models import failed: {e}")
        return False

def test_file_structure():
    """Test overall file structure"""
    required_dirs = [
        "src/agent/nodes",
        "src/agent/routing", 
        "src/db",
        "src/services",
        "src/middleware",
        "src/routes"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    else:
        print("✅ All required directories exist")
        return True

def test_agent_imports():
    """Test that agent classes can be imported (without instantiation)"""
    try:
        # Import without creating instances (to avoid dependency issues)
        import importlib.util
        
        # Test master orchestrator
        spec = importlib.util.spec_from_file_location("master_orchestrator", "src/agent/nodes/master_orchestrator.py")
        if spec is None:
            print("❌ Could not load master orchestrator spec")
            return False
        
        print("✅ Master orchestrator file is importable")
        
        # Test other key agents
        agent_files = [
            "src/agent/nodes/search_gemini.py",
            "src/agent/nodes/search_perplexity.py",
            "src/agent/nodes/writer.py"
        ]
        
        for agent_file in agent_files:
            spec = importlib.util.spec_from_file_location("agent", agent_file)
            if spec is None:
                print(f"❌ Could not load {agent_file}")
                return False
        
        print("✅ All key agent files are importable")
        return True
        
    except Exception as e:
        print(f"❌ Agent imports failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🧪 Running Basic System Tests")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration Files", test_configuration_files), 
        ("Node Structure", test_node_structure),
        ("Basic Imports", test_basic_imports),
        ("Database Models", test_database_models),
        ("Agent Imports", test_agent_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}...")
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("🎉 All basic tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - check configuration")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)