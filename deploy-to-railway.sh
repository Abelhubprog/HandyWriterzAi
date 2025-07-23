#!/bin/bash

# Railway Deployment Script for MultiAgent HandyWriterz
# This script automates the deployment process to Railway

set -e  # Exit on error

echo "🚀 Starting Railway deployment for MultiAgent HandyWriterz..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_error "Railway CLI not found. Installing..."
    npm install -g @railway/cli
    if [ $? -ne 0 ]; then
        print_error "Failed to install Railway CLI. Please install manually:"
        print_error "npm install -g @railway/cli"
        exit 1
    fi
fi

print_status "Railway CLI found"

# Check if user is logged in to Railway
if ! railway whoami &> /dev/null; then
    print_warning "Not logged in to Railway. Please log in:"
    railway login
    if [ $? -ne 0 ]; then
        print_error "Railway login failed"
        exit 1
    fi
fi

print_status "Railway authentication verified"

# Step 1: Create or link Railway project
print_step "Setting up Railway project..."

if [ ! -f ".railway" ]; then
    print_warning "No Railway project found. Creating new project..."
    echo "Please choose:"
    echo "1. Create new project"
    echo "2. Link to existing project"
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            railway new --name "multiagent-handywriterz"
            ;;
        2)
            railway link
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
else
    print_status "Railway project already linked"
fi

# Step 2: Add databases
print_step "Setting up databases..."

# Add PostgreSQL
print_status "Adding PostgreSQL database..."
railway add postgresql || print_warning "PostgreSQL might already exist"

# Add Redis
print_status "Adding Redis cache..."
railway add redis || print_warning "Redis might already exist"

# Wait for databases to be ready
print_status "Waiting for databases to initialize..."
sleep 10

# Step 3: Enable pgvector extension
print_step "Enabling pgvector extension..."
DATABASE_URL=$(railway variables get DATABASE_URL 2>/dev/null || echo "")

if [ -n "$DATABASE_URL" ]; then
    print_status "Enabling pgvector extension in PostgreSQL..."
    railway run psql "$DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS vector;" || print_warning "pgvector extension might already exist"
else
    print_warning "DATABASE_URL not available yet. You may need to enable pgvector manually later:"
    print_warning "railway run psql \$DATABASE_URL -c \"CREATE EXTENSION IF NOT EXISTS vector;\""
fi

# Step 4: Set environment variables
print_step "Setting up environment variables..."

# Check if environment file exists
if [ -f ".env.railway" ]; then
    print_status "Found .env.railway file. Please set the following required variables:"
    echo ""
    echo "Required API Keys (get these from respective providers):"
    echo "- OPENAI_API_KEY"
    echo "- ANTHROPIC_API_KEY" 
    echo "- GEMINI_API_KEY"
    echo "- PERPLEXITY_API_KEY"
    echo ""
    
    # Prompt for API keys
    read -p "Enter OpenAI API Key: " OPENAI_KEY
    read -p "Enter Anthropic API Key: " ANTHROPIC_KEY
    read -p "Enter Gemini API Key: " GEMINI_KEY
    read -p "Enter Perplexity API Key: " PERPLEXITY_KEY
    
    # Set API keys
    railway variables set OPENAI_API_KEY="$OPENAI_KEY"
    railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_KEY"
    railway variables set GEMINI_API_KEY="$GEMINI_KEY"
    railway variables set PERPLEXITY_API_KEY="$PERPLEXITY_KEY"
    
    # Set other required variables
    print_status "Setting additional environment variables..."
    railway variables set NODE_ENV=production
    railway variables set LOG_LEVEL=info
    railway variables set ENABLE_DEBUG_LOGGING=false
    
    # CPU optimization
    railway variables set TORCH_CPU_ONLY=true
    railway variables set OMP_NUM_THREADS=2
    railway variables set MKL_NUM_THREADS=2
    railway variables set CUDA_VISIBLE_DEVICES=""
    
    # Generate secure secrets
    JWT_SECRET=$(openssl rand -base64 32)
    ENCRYPTION_KEY=$(openssl rand -base64 32)
    SESSION_SECRET=$(openssl rand -base64 32)
    
    railway variables set JWT_SECRET="$JWT_SECRET"
    railway variables set ENCRYPTION_KEY="$ENCRYPTION_KEY"
    railway variables set SESSION_SECRET="$SESSION_SECRET"
    railway variables set USE_SECURE_COOKIES=true
    
    # Rate limiting
    railway variables set RATE_LIMIT_REQUESTS_PER_MINUTE=60
    railway variables set RATE_LIMIT_BURST=10
    railway variables set RATE_LIMIT=1000
    
    print_status "Environment variables set successfully"
else
    print_warning ".env.railway file not found. Using default environment setup."
fi

# Step 5: Deploy the application
print_step "Deploying application to Railway..."

# Deploy backend
print_status "Deploying backend service..."
railway up --detach

if [ $? -eq 0 ]; then
    print_status "Backend deployment initiated successfully"
else
    print_error "Backend deployment failed"
    exit 1
fi

# Wait for deployment
print_status "Waiting for deployment to complete..."
sleep 30

# Step 6: Run database migrations
print_step "Running database migrations..."
railway run python -m alembic upgrade head

if [ $? -eq 0 ]; then
    print_status "Database migrations completed successfully"
else
    print_warning "Database migrations failed. You may need to run them manually:"
    print_warning "railway run python -m alembic upgrade head"
fi

# Step 7: Generate domain
print_step "Setting up domain..."
DOMAIN=$(railway domain 2>/dev/null || echo "")

if [ -n "$DOMAIN" ]; then
    print_status "Domain generated: $DOMAIN"
    
    # Update CORS settings with the new domain
    railway variables set NEXT_PUBLIC_BACKEND_URL="https://$DOMAIN"
    railway variables set BACKEND_URL="https://$DOMAIN"
    railway variables set CORS_ALLOW_ORIGIN="https://$DOMAIN"
    
    print_status "CORS settings updated with new domain"
else
    print_warning "Could not generate domain automatically. You can do this later with: railway domain"
fi

# Step 8: Setup monitoring and logs
print_step "Setting up monitoring..."

print_status "You can monitor your deployment with:"
echo "  railway logs        # View application logs"
echo "  railway status      # Check service status"
echo "  railway shell       # Access deployment shell"
echo "  railway open        # Open in browser"

# Step 9: Optional - Deploy frontend and workers
echo ""
print_step "Optional: Deploy additional services"
echo "Would you like to deploy additional services?"
echo "1. Frontend (Next.js)"
echo "2. Celery Workers"
echo "3. Both"
echo "4. Skip"
read -p "Enter choice (1-4): " service_choice

case $service_choice in
    1|3)
        print_status "Setting up frontend service..."
        railway service create frontend
        
        # Deploy frontend from the frontend directory
        if [ -d "frontend/web/HandyWriterz" ]; then
            cd frontend/web/HandyWriterz
            railway service link frontend
            railway up --detach
            cd ../../..
            print_status "Frontend deployment initiated"
        else
            print_warning "Frontend directory not found. Skipping frontend deployment."
        fi
        ;;
esac

case $service_choice in
    2|3)
        print_status "Setting up Celery worker service..."
        railway service create celery-worker
        railway service link celery-worker
        
        # Set worker-specific variables
        railway variables set --service celery-worker START_COMMAND="celery -A src.workers.celery_app worker --loglevel=info --concurrency=2"
        railway variables set --service celery-worker SERVICE_NAME="celery-worker"
        
        # Deploy worker
        railway up --detach --service celery-worker
        print_status "Celery worker deployment initiated"
        ;;
esac

# Final steps
print_step "Deployment Summary"
echo ""
print_status "✅ Railway deployment completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Check deployment status: railway status"
echo "2. View logs: railway logs"
echo "3. Test your API: curl https://your-domain.railway.app/health"
echo "4. Monitor resources in Railway dashboard"
echo ""

if [ -n "$DOMAIN" ]; then
    echo "🌐 Your API is available at: https://$DOMAIN"
    echo "📚 API Documentation: https://$DOMAIN/docs"
    echo "🔍 Health Check: https://$DOMAIN/health"
else
    echo "🌐 Get your domain with: railway domain"
fi

echo ""
echo "💡 Useful Commands:"
echo "  railway logs                    # View real-time logs"
echo "  railway shell                   # Access deployment shell"
echo "  railway variables               # View environment variables"
echo "  railway open                    # Open Railway dashboard"
echo "  railway status                  # Check all services status"
echo ""

print_status "Deployment script completed successfully! 🎉"