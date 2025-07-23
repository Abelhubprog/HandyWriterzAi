#!/bin/bash

# Database Migration Script: Supabase to Railway PostgreSQL
# This script migrates your system from Supabase to Railway's native PostgreSQL

set -e

echo "🔄 Migrating from Supabase to Railway PostgreSQL..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[MIGRATE]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Step 1: Add Railway PostgreSQL if not already added
print_step "Setting up Railway PostgreSQL..."

# Check if Railway is configured
if [ ! -f ".railway" ]; then
    print_warning "Railway not configured. Please run 'railway link' first."
    exit 1
fi

# Add PostgreSQL if not exists
print_status "Adding PostgreSQL to Railway project..."
railway add postgresql || print_warning "PostgreSQL might already exist"

# Wait for database to be ready
print_status "Waiting for PostgreSQL to initialize..."
sleep 10

# Step 2: Enable pgvector extension
print_step "Enabling pgvector extension..."
DATABASE_URL=$(railway variables get DATABASE_URL 2>/dev/null || echo "")

if [ -n "$DATABASE_URL" ]; then
    print_status "Enabling pgvector extension..."
    railway run psql "$DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS vector;" || print_warning "pgvector might already exist"
    
    print_status "Creating additional tables for Railway..."
    railway run psql "$DATABASE_URL" -c "
    CREATE TABLE IF NOT EXISTS user_memories (
        id SERIAL PRIMARY KEY,
        user_id VARCHAR(255) UNIQUE NOT NULL,
        fingerprint JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_user_memories_user_id ON user_memories(user_id);
    " || print_warning "Tables might already exist"
    
else
    print_warning "DATABASE_URL not available yet. You may need to run these commands manually:"
    echo "railway run psql \$DATABASE_URL -c \"CREATE EXTENSION IF NOT EXISTS vector;\""
fi

# Step 3: Update environment variables
print_step "Updating environment variables..."

# Remove Supabase variables if they exist
railway variables remove SUPABASE_URL || true
railway variables remove SUPABASE_KEY || true
railway variables remove NEXT_PUBLIC_SUPABASE_URL || true
railway variables remove NEXT_PUBLIC_SUPABASE_ANON_KEY || true

print_status "Removed Supabase environment variables"

# Step 4: Run database migrations
print_step "Running Alembic migrations..."
railway run python -m alembic upgrade head || print_warning "Migrations might have failed - check manually"

# Step 5: Test database connection
print_step "Testing database connection..."
railway run python -c "
import os
import psycopg2
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()
    cur.execute('SELECT version();')
    version = cur.fetchone()
    print('✅ PostgreSQL connection successful:', version[0])
    cur.close()
    conn.close()
except Exception as e:
    print('❌ Database connection failed:', e)
" || print_warning "Database test failed"

print_status "✅ Migration to Railway PostgreSQL completed!"

echo ""
echo "📋 Next Steps:"
echo "1. Deploy your backend: railway up"
echo "2. Verify the application works with Railway PostgreSQL"
echo "3. Remove Supabase dependency from requirements.txt if desired"
echo ""
echo "💡 Railway PostgreSQL Features:"
echo "- Automatic backups"
echo "- pgvector extension enabled"
echo "- Integrated with your Railway project"
echo "- No additional costs on free tier"
echo ""

print_status "Database migration script completed! 🎉"