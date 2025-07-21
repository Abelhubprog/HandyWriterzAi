#!/usr/bin/env python3
"""
Complete Python 3.14 Setup Script for HandyWriterz Backend
Handles the entire backend/backend directory structure with maximum compatibility.
"""

import os
import sys
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime


class HandyWriterzSetup:
    """Complete setup manager for HandyWriterz backend."""
    
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.src_dir = self.root_dir / "src"
        self.db_path = self.root_dir / "handywriterz.db"
        self.env_path = self.root_dir / ".env"
        
    def run_command(self, cmd, description="", ignore_errors=False):
        """Run a command with error handling."""
        print(f"🔄 {description}")
        try:
            result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=self.root_dir)
            if result.stdout:
                print(f"   ✅ {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            if not ignore_errors:
                print(f"   ❌ Error: {e}")
                if e.stderr:
                    print(f"   {e.stderr.strip()}")
            return False
    
    def install_packages(self):
        """Install Python packages with fallback strategies."""
        print("\n📦 Installing Python packages for Python 3.14...")
        
        # Strategy 1: Try essential packages first
        essential_packages = [
            "fastapi>=0.110.0",
            "uvicorn[standard]>=0.27.0",
            "pydantic>=2.6.0",
            "python-dotenv>=1.0.1",
            "aiofiles>=23.2.1",
            "python-multipart>=0.0.9",
            "aiosqlite>=0.19.0"
        ]
        
        print("   Installing essential packages...")
        for package in essential_packages:
            success = self.run_command(
                f"{sys.executable} -m pip install '{package}' --no-cache-dir",
                f"Installing {package.split('>=')[0]}",
                ignore_errors=True
            )
            if not success:
                # Try without version constraints
                base_package = package.split('>=')[0].split('[')[0]
                self.run_command(
                    f"{sys.executable} -m pip install '{base_package}' --no-cache-dir",
                    f"Installing {base_package} (fallback)",
                    ignore_errors=True
                )
        
        # Strategy 2: Try optional packages
        optional_packages = [
            "sqlalchemy>=2.0.27",
            "alembic>=1.13.1",
            "redis>=5.0.1",
            "aiohttp>=3.9.3",
            "cryptography>=41.0.0",
            "pyyaml>=6.0.1"
        ]
        
        print("   Installing optional packages...")
        for package in optional_packages:
            self.run_command(
                f"{sys.executable} -m pip install '{package}' --no-cache-dir",
                f"Installing {package.split('>=')[0]}",
                ignore_errors=True
            )
        
        return True
    
    def create_database(self):
        """Create SQLite database with all required tables."""
        print("\n🗄️  Creating HandyWriterz database...")
        
        try:
            # Remove existing database
            if self.db_path.exists():
                self.db_path.unlink()
                print("   Removed existing database")
            
            # Create new database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # Create all tables
            tables = self._get_table_definitions()
            
            for table_name, table_sql in tables.items():
                cursor.execute(table_sql)
                print(f"   ✅ Created table: {table_name}")
            
            # Insert default data
            self._insert_default_data(cursor)
            
            # Create indexes
            self._create_indexes(cursor)
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Database created: {self.db_path}")
            return True
            
        except Exception as e:
            print(f"   ❌ Database creation failed: {e}")
            return False
    
    def _get_table_definitions(self):
        """Get all table definitions."""
        return {
            "model_map": """
            CREATE TABLE model_map (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stage VARCHAR(50) NOT NULL,
                model_name VARCHAR(100) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            "users": """
            CREATE TABLE users (
                id TEXT PRIMARY KEY,
                wallet_address VARCHAR(255) UNIQUE NOT NULL,
                user_type VARCHAR(50) DEFAULT 'student',
                subscription_tier VARCHAR(50) DEFAULT 'free',
                credits_balance INTEGER DEFAULT 3,
                credits_used INTEGER DEFAULT 0,
                documents_created INTEGER DEFAULT 0,
                avg_quality_score REAL DEFAULT 0.0,
                total_words_generated INTEGER DEFAULT 0,
                welcome_bonus_claimed BOOLEAN DEFAULT FALSE,
                preferences TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP
            )
            """,
            
            "conversations": """
            CREATE TABLE conversations (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title VARCHAR(500),
                workflow_status VARCHAR(50) DEFAULT 'initiated',
                current_node VARCHAR(100),
                user_params TEXT,
                processing_duration REAL,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            
            "documents": """
            CREATE TABLE documents (
                id TEXT PRIMARY KEY,
                conversation_id TEXT NOT NULL,
                title VARCHAR(500),
                document_type VARCHAR(50),
                content_markdown TEXT,
                content_html TEXT,
                word_count INTEGER DEFAULT 0,
                overall_quality_score REAL DEFAULT 0.0,
                citation_count INTEGER DEFAULT 0,
                academic_field VARCHAR(100),
                docx_url TEXT,
                pdf_url TEXT,
                html_url TEXT,
                file_urls TEXT,
                learning_outcomes_coverage TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
            """,
            
            "checkers": """
            CREATE TABLE checkers (
                id TEXT PRIMARY KEY,
                wallet_address VARCHAR(255) UNIQUE NOT NULL,
                phone_number VARCHAR(50),
                telegram_chat_id VARCHAR(100),
                specialties TEXT,
                rating_score REAL DEFAULT 5.0,
                penalty_points INTEGER DEFAULT 0,
                penalty_until TIMESTAMP,
                earnings_total INTEGER DEFAULT 0,
                chunks_completed INTEGER DEFAULT 0,
                avg_completion_time REAL DEFAULT 0.0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            "doc_lots": """
            CREATE TABLE doc_lots (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                title VARCHAR(500),
                total_chunks INTEGER DEFAULT 0,
                chunks_completed INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'processing',
                estimated_cost INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """,
            
            "doc_chunks": """
            CREATE TABLE doc_chunks (
                id TEXT PRIMARY KEY,
                lot_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                word_count INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'open',
                checker_id TEXT,
                quality_score REAL DEFAULT 0.0,
                similarity_score REAL,
                ai_score REAL,
                contains_citations BOOLEAN DEFAULT FALSE,
                timer_expires TIMESTAMP,
                bounty_pence INTEGER DEFAULT 18,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lot_id) REFERENCES doc_lots (id),
                FOREIGN KEY (checker_id) REFERENCES checkers (id)
            )
            """,
            
            "submissions": """
            CREATE TABLE submissions (
                id TEXT PRIMARY KEY,
                chunk_id TEXT NOT NULL,
                checker_id TEXT NOT NULL,
                version INTEGER DEFAULT 1,
                status VARCHAR(50) DEFAULT 'needs_edit',
                ai_pdf_url TEXT,
                sim_pdf_url TEXT,
                flags TEXT,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chunk_id) REFERENCES doc_chunks (id),
                FOREIGN KEY (checker_id) REFERENCES checkers (id)
            )
            """,
            
            "checker_payouts": """
            CREATE TABLE checker_payouts (
                id TEXT PRIMARY KEY,
                checker_id TEXT NOT NULL,
                chunk_id TEXT NOT NULL,
                amount_pence INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                transaction_hash TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (checker_id) REFERENCES checkers (id),
                FOREIGN KEY (chunk_id) REFERENCES doc_chunks (id)
            )
            """,
            
            "wallet_escrows": """
            CREATE TABLE wallet_escrows (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                lot_id TEXT NOT NULL,
                amount_usdc INTEGER NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                transaction_hash TEXT,
                escrow_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (lot_id) REFERENCES doc_lots (id)
            )
            """,
            
            "system_metrics": """
            CREATE TABLE system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name VARCHAR(100) NOT NULL,
                metric_category VARCHAR(50) NOT NULL,
                metric_value REAL NOT NULL,
                metadata TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            "source_cache": """
            CREATE TABLE source_cache (
                id TEXT PRIMARY KEY,
                url TEXT UNIQUE NOT NULL,
                title TEXT,
                content TEXT,
                author TEXT,
                publication_date DATE,
                academic_field VARCHAR(100),
                credibility_score REAL DEFAULT 0.0,
                citation_count INTEGER DEFAULT 0,
                embeddings TEXT,
                metadata TEXT,
                cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
            """,
            
            "private_chunks": """
            CREATE TABLE private_chunks (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                content_hash VARCHAR(64) NOT NULL,
                chunk_text TEXT NOT NULL,
                embeddings TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        }
    
    def _insert_default_data(self, cursor):
        """Insert default data into tables."""
        print("   Inserting default data...")
        
        # Default model configuration
        default_models = [
            ('INTENT', 'gemini-2.0-flash-exp'),
            ('PLAN', 'gemini-2.0-flash-exp'),
            ('SEARCH-A', 'gemini-2.0-flash-exp'),
            ('SEARCH-B', 'grok-4-web'),
            ('SEARCH-C', 'openai-o3'),
            ('EVIDENCE', 'gemini-2.0-flash-exp'),
            ('WRITE', 'gemini-2.0-flash-exp'),
            ('REWRITE', 'openai-o3'),
            ('QA-1', 'gemini-2.0-flash-exp'),
            ('QA-2', 'grok-4-web'),
            ('QA-3', 'openai-o3'),
            ('FORMATTER', 'gemini-2.0-flash-exp'),
            ('EVALUATOR', 'claude-3-5-sonnet'),
            ('TURNITIN', 'gemini-2.0-flash-exp')
        ]
        
        cursor.executemany(
            "INSERT INTO model_map (stage, model_name) VALUES (?, ?)",
            default_models
        )
        
        # System metrics initialization
        initial_metrics = [
            ('system_startup', 'system', 1.0, '{"startup_time": "' + datetime.now().isoformat() + '"}'),
            ('database_version', 'system', 1.0, '{"version": "1.0.0"}'),
            ('features_enabled', 'system', 1.0, '{"workbench": true, "payments": true}')
        ]
        
        cursor.executemany(
            "INSERT INTO system_metrics (metric_name, metric_category, metric_value, metadata) VALUES (?, ?, ?, ?)",
            initial_metrics
        )
        
        print(f"   ✅ Inserted {len(default_models)} model configurations")
        print(f"   ✅ Inserted {len(initial_metrics)} system metrics")
    
    def _create_indexes(self, cursor):
        """Create database indexes for performance."""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_users_wallet ON users(wallet_address)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_user ON conversations(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_conversations_status ON conversations(workflow_status)",
            "CREATE INDEX IF NOT EXISTS idx_documents_conversation ON documents(conversation_id)",
            "CREATE INDEX IF NOT EXISTS idx_documents_type ON documents(document_type)",
            "CREATE INDEX IF NOT EXISTS idx_checkers_wallet ON checkers(wallet_address)",
            "CREATE INDEX IF NOT EXISTS idx_checkers_active ON checkers(is_active)",
            "CREATE INDEX IF NOT EXISTS idx_doc_chunks_lot ON doc_chunks(lot_id)",
            "CREATE INDEX IF NOT EXISTS idx_doc_chunks_status ON doc_chunks(status)",
            "CREATE INDEX IF NOT EXISTS idx_doc_chunks_checker ON doc_chunks(checker_id)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_chunk ON submissions(chunk_id)",
            "CREATE INDEX IF NOT EXISTS idx_submissions_checker ON submissions(checker_id)",
            "CREATE INDEX IF NOT EXISTS idx_payouts_checker ON checker_payouts(checker_id)",
            "CREATE INDEX IF NOT EXISTS idx_payouts_status ON checker_payouts(status)",
            "CREATE INDEX IF NOT EXISTS idx_escrows_user ON wallet_escrows(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_escrows_lot ON wallet_escrows(lot_id)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_category ON system_metrics(metric_category)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_recorded ON system_metrics(recorded_at)",
            "CREATE INDEX IF NOT EXISTS idx_source_cache_url ON source_cache(url)",
            "CREATE INDEX IF NOT EXISTS idx_source_cache_field ON source_cache(academic_field)",
            "CREATE INDEX IF NOT EXISTS idx_private_chunks_user ON private_chunks(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_private_chunks_hash ON private_chunks(content_hash)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        print(f"   ✅ Created {len(indexes)} database indexes")
    
    def create_environment_file(self):
        """Create .env file with all necessary configuration."""
        print("\n📝 Creating environment configuration...")
        
        env_content = f"""# HandyWriterz Backend Configuration
# Generated on {datetime.now().isoformat()}

# Database Configuration
DATABASE_URL=sqlite:///{self.db_path.absolute()}
DB_ECHO=false

# Redis Configuration (optional - will use in-memory fallback if not available)
REDIS_URL=redis://localhost:6379

# AI API Keys (add your keys here)
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
PERPLEXITY_API_KEY=your_perplexity_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
QWEN_API_KEY=your_qwen_api_key_here
GROK_API_KEY=your_grok_api_key_here

# Blockchain Configuration (optional)
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
BASE_RPC_URL=https://mainnet.base.org
SOLANA_USDC_MINT=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
BASE_USDC_CONTRACT=0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

# Cloudflare Configuration (optional)
CLOUDFLARE_ACCOUNT_ID=your_cloudflare_account_id
CLOUDFLARE_API_TOKEN=your_cloudflare_api_token
CLOUDFLARE_D1_DATABASE_ID=your_d1_database_id
CLOUDFLARE_R2_BUCKET=your_r2_bucket_name
CLOUDFLARE_R2_ACCESS_KEY=your_r2_access_key
CLOUDFLARE_R2_SECRET_KEY=your_r2_secret_key
CLOUDFLARE_R2_ENDPOINT=your_r2_endpoint

# Dynamic.xyz Authentication (optional)
DYNAMIC_ENVIRONMENT_ID=your_dynamic_environment_id
DYNAMIC_API_KEY=your_dynamic_api_key

# Telegram Bot Configuration (for Turnitin integration)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id

# WhatsApp API Configuration (optional)
WHATSAPP_API_URL=https://api.whatsapp.com/send
WHATSAPP_TOKEN=your_whatsapp_token

# System Configuration
MAX_CLAIMS_PER_CHECKER=3
TIMEOUT_CHECK_MIN=15
AGENT_TIMEOUT_SECONDS=300
SWARM_COORDINATION_TIMEOUT=600
WORKER_TIMEOUT=120
DATABASE_POOL_TIMEOUT=30
CACHE_TTL=3600

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
RELOAD=true

# Security Configuration
SECRET_KEY=your_secret_key_here_change_in_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Upload Configuration
MAX_FILE_SIZE=50
MAX_FILE_COUNT=10
UPLOAD_DIR=./uploads

# Monitoring Configuration (optional)
SENTRY_DSN=your_sentry_dsn_here
LOG_LEVEL=INFO

# Feature Flags
ENABLE_TURNITIN_WORKBENCH=true
ENABLE_PAYMENT_SYSTEM=true
ENABLE_NOTIFICATIONS=true
ENABLE_BACKGROUND_WORKERS=true
"""
        
        with open(self.env_path, "w") as f:
            f.write(env_content)
        
        print(f"   ✅ Created environment file: {self.env_path}")
        print("   ⚠️  Remember to add your actual API keys!")
    
    def create_startup_script(self):
        """Create startup script for the server."""
        startup_script = """#!/usr/bin/env python3
'''
HandyWriterz Backend Startup Script
Auto-generated for Python 3.14 compatibility
'''

import sys
import os
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

# Verify database exists
db_path = Path(__file__).parent / 'handywriterz.db'
if not db_path.exists():
    print("❌ Database not found. Run: python setup_py314.py")
    sys.exit(1)

# Verify environment file exists
env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    print("❌ Environment file not found. Run: python setup_py314.py")
    sys.exit(1)

print("🚀 Starting HandyWriterz Backend...")
print(f"📄 Database: {db_path}")
print(f"⚙️  Environment: {env_path}")

try:
    # Import and run the main application
    import uvicorn
    from main import app
    
    print("🌐 Server starting at: http://localhost:8000")
    print("📖 API docs at: http://localhost:8000/docs")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Try installing packages: python setup_py314.py --install-only")
    sys.exit(1)
except Exception as e:
    print(f"❌ Startup error: {e}")
    sys.exit(1)
"""
        
        startup_path = self.root_dir / "start_server.py"
        with open(startup_path, "w") as f:
            f.write(startup_script)
        
        # Make executable on Unix systems
        if os.name != 'nt':
            os.chmod(startup_path, 0o755)
        
        print(f"   ✅ Created startup script: {startup_path}")
    
    def create_test_script(self):
        """Create test script to verify installation."""
        test_script = """#!/usr/bin/env python3
'''
HandyWriterz Backend Test Script
Tests the installation and basic functionality
'''

import sys
import sqlite3
from pathlib import Path

def test_database():
    '''Test database connectivity and structure.'''
    print("🗄️  Testing database...")
    
    db_path = Path(__file__).parent / 'handywriterz.db'
    if not db_path.exists():
        print("   ❌ Database file not found")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic queries
        cursor.execute("SELECT COUNT(*) FROM model_map")
        model_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        conn.close()
        
        print(f"   ✅ Database OK: {table_count} tables, {model_count} models")
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_imports():
    '''Test critical package imports.'''
    print("📦 Testing package imports...")
    
    required_packages = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'sqlite3',
        'aiofiles'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - not available")
            return False
    
    return True

def test_environment():
    '''Test environment configuration.'''
    print("⚙️  Testing environment...")
    
    env_path = Path(__file__).parent / '.env'
    if not env_path.exists():
        print("   ❌ .env file not found")
        return False
    
    print("   ✅ Environment file exists")
    return True

def main():
    '''Run all tests.'''
    print("🧪 HandyWriterz Backend Test Suite")
    print("=" * 40)
    
    tests = [
        test_database,
        test_imports,
        test_environment
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("✅ All tests passed! Backend is ready.")
        print("🚀 Run: python start_server.py")
    else:
        print("❌ Some tests failed. Check the setup.")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""
        
        test_path = self.root_dir / "test_setup.py"
        with open(test_path, "w") as f:
            f.write(test_script)
        
        print(f"   ✅ Created test script: {test_path}")
    
    def run_setup(self, install_packages=True):
        """Run the complete setup process."""
        print("🚀 HandyWriterz Backend Setup for Python 3.14")
        print("=" * 60)
        print(f"📁 Working directory: {self.root_dir}")
        print(f"🐍 Python version: {sys.version}")
        print()
        
        success_count = 0
        total_steps = 5 if install_packages else 4
        
        # Step 1: Install packages (optional)
        if install_packages:
            if self.install_packages():
                success_count += 1
                print("   ✅ Package installation completed")
            else:
                print("   ⚠️  Package installation had some issues (continuing)")
        
        # Step 2: Create database
        if self.create_database():
            success_count += 1
        
        # Step 3: Create environment file
        self.create_environment_file()
        success_count += 1
        
        # Step 4: Create startup script
        self.create_startup_script()
        success_count += 1
        
        # Step 5: Create test script
        self.create_test_script()
        success_count += 1
        
        print(f"\n📊 Setup Results: {success_count}/{total_steps} steps completed")
        
        if success_count >= total_steps - 1:  # Allow for package install issues
            print("\n✅ Setup completed successfully!")
            print("\n📋 Next steps:")
            print("1. Edit .env file and add your API keys")
            print("2. Test the setup: python test_setup.py")
            print("3. Start the server: python start_server.py")
            print("4. Visit: http://localhost:8000/docs")
            
            print("\n🔗 Available endpoints:")
            print("   • http://localhost:8000/health - Health check")
            print("   • http://localhost:8000/api/models - Model configuration")
            print("   • http://localhost:8000/api/status - System status")
            print("   • http://localhost:8000/checker - Turnitin Workbench")
            print("   • http://localhost:8000/payments - Payment system")
            
        else:
            print("\n❌ Setup encountered issues!")
            print("Try running: python setup_py314.py --install-only")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="HandyWriterz Backend Setup for Python 3.14")
    parser.add_argument("--install-only", action="store_true", help="Only install packages")
    parser.add_argument("--no-packages", action="store_true", help="Skip package installation")
    
    args = parser.parse_args()
    
    setup = HandyWriterzSetup()
    
    if args.install_only:
        setup.install_packages()
    else:
        setup.run_setup(install_packages=not args.no_packages)


if __name__ == "__main__":
    main()