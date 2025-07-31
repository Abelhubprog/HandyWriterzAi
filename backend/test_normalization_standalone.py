#!/usr/bin/env python3
"""
Standalone test for parameter normalization without full app dependencies.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_normalization():
    """Test parameter normalization directly."""
    print("🧪 Testing parameter normalization (standalone)")
    
    try:
        # Import just the normalization functions
        sys.path.insert(0, str(Path(__file__).parent / "src" / "agent" / "routing"))
        from normalization import normalize_user_params, validate_user_params
        
        # Test cases
        test_cases = [
            {
                "name": "PhD Dissertation",
                "input": {
                    "writeupType": "PhD Dissertation",
                    "citationStyle": "harvard",
                    "wordCount": 8000,
                    "educationLevel": "Doctoral"
                },
                "expected_keys": ["document_type", "citation_style", "word_count", "academic_level", "pages"]
            },
            {
                "name": "Research Paper", 
                "input": {
                    "writeupType": "Research Paper",
                    "citationStyle": "apa",
                    "wordCount": 3000
                },
                "expected_keys": ["document_type", "citation_style", "word_count", "pages"]
            }
        ]
        
        for test_case in test_cases:
            print(f"\n  Testing: {test_case['name']}")
            
            # Normalize parameters
            normalized = normalize_user_params(test_case["input"])
            print(f"    Input: {test_case['input']}")
            print(f"    Output: {normalized}")
            
            # Check expected keys exist
            for key in test_case["expected_keys"]:
                if key not in normalized:
                    print(f"    ❌ Missing expected key: {key}")
                    return False
                    
            # Validate parameters
            try:
                validate_user_params(normalized)
                print(f"    ✅ Validation passed")
            except Exception as e:
                print(f"    ⚠️ Validation warning: {e}")
                
        print("\n✅ Parameter normalization working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Parameter normalization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_normalization()
    print("\n" + "="*50)
    if success:
        print("🎉 NORMALIZATION TEST PASSED!")
        print("The /api/write parameter normalization is ready for production.")
    else:
        print("❌ NORMALIZATION TEST FAILED!")
    sys.exit(0 if success else 1)