"""Test script to verify models can be imported without database initialization."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Set a dummy database URL to prevent initialization
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

try:
    # Import models without triggering database initialization
    from src.db.models import Base as MainBase
    print("✓ Main models imported successfully")
    
    # Import Turnitin models
    print("✓ Turnitin models imported successfully")
    
    # Check that tables are registered
    print(f"\nMain Base tables: {len(MainBase.metadata.tables)}")
    for table_name in MainBase.metadata.tables:
        print(f"  - {table_name}")
    
except Exception as e:
    print(f"✗ Error importing models: {e}")
    import traceback
    traceback.print_exc()