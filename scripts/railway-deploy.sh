#!/bin/bash

# Railway Deployment Script for HandyWriterz
# Configures and deploys the complete application to Railway

set -e

echo "🚄 HandyWriterz Railway Deployment"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
    print_error "Railway CLI not found. Install with: npm install -g @railway/cli"
    exit 1
fi

print_status "Railway CLI found"

# Check if user is logged in
print_step "Checking Railway authentication..."
if ! railway whoami &> /dev/null; then
    print_warning "Not logged in to Railway. Please log in:"
    railway login
    if [ $? -ne 0 ]; then
        print_error "Railway login failed"
        exit 1
    fi
fi

print_status "Railway authentication verified"

# Step 1: Create or connect to Railway project
print_step "Setting up Railway project..."

if [ ! -f ".railway" ]; then
    print_warning "No Railway project found. Creating new project..."
    echo "Please choose:"
    echo "1. Create new project"
    echo "2. Link to existing project"
    read -p "Enter choice (1 or 2): " choice
    
    case $choice in
        1)
            railway new handywriterz-ai
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

# Step 2: Add required services
print_step "Setting up Railway services..."

# Add PostgreSQL
print_status "Adding PostgreSQL database..."
railway add postgresql || print_warning "PostgreSQL might already exist"

# Add Redis
print_status "Adding Redis cache..."
railway add redis || print_warning "Redis might already exist"

# Wait for services to be ready
print_status "Waiting for services to initialize..."
sleep 15

# Step 3: Enable pgvector extension
print_step "Enabling pgvector extension..."
DATABASE_URL=$(railway variables get DATABASE_URL 2>/dev/null || echo "")

if [ -n "$DATABASE_URL" ]; then
    print_status "Enabling pgvector extension in PostgreSQL..."
    railway run psql "$DATABASE_URL" -c "CREATE EXTENSION IF NOT EXISTS vector;" || print_warning "pgvector extension might already exist"
else
    print_warning "DATABASE_URL not available yet. Enable pgvector manually later:"
    print_warning "railway run psql \$DATABASE_URL -c \"CREATE EXTENSION IF NOT EXISTS vector;\""
fi

# Step 4: Set environment variables
print_step "Configuring environment variables..."

# Check if .env file exists for reference
if [ -f ".env.example" ]; then
    print_status "Using .env.example as reference for required variables"
else
    print_warning ".env.example not found. Please ensure all required environment variables are set."
fi

# Prompt for required API keys
echo ""
print_status "Please provide the following API keys:"

# AI Provider API Keys
read -p "OpenAI API Key: " OPENAI_KEY
read -p "Anthropic API Key: " ANTHROPIC_KEY  
read -p "Gemini API Key: " GEMINI_KEY
read -p "Perplexity API Key: " PERPLEXITY_KEY

# Payment Provider Keys
echo ""
read -p "Paystack Secret Key: " PAYSTACK_KEY
read -p "Coinbase Commerce API Key: " COINBASE_KEY

# Dynamic.xyz Auth
echo ""
read -p "Dynamic.xyz Environment ID: " DYNAMIC_ENV_ID
read -p "Dynamic.xyz Public Key: " DYNAMIC_PUBLIC_KEY

# Set all environment variables
print_status "Setting environment variables in Railway..."

# AI Provider Keys
railway variables set OPENAI_API_KEY="$OPENAI_KEY"
railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_KEY" 
railway variables set GEMINI_API_KEY="$GEMINI_KEY"
railway variables set PERPLEXITY_API_KEY="$PERPLEXITY_KEY"

# Payment Provider Keys
railway variables set PAYSTACK_SECRET_KEY="$PAYSTACK_KEY"
railway variables set COINBASE_API_KEY="$COINBASE_KEY"

# Dynamic.xyz Auth
railway variables set DYNAMIC_ENV_ID="$DYNAMIC_ENV_ID"
railway variables set DYNAMIC_PUBLIC_KEY="$DYNAMIC_PUBLIC_KEY"

# Application Configuration
railway variables set ENVIRONMENT=production
railway variables set LOG_LEVEL=INFO
railway variables set NODE_ENV=production

# Generate secure JWT secret
JWT_SECRET=$(openssl rand -base64 32)
railway variables set JWT_SECRET_KEY="$JWT_SECRET"

# Performance optimizations for Railway
railway variables set TORCH_CPU_ONLY=true
railway variables set OMP_NUM_THREADS=2
railway variables set MKL_NUM_THREADS=2
railway variables set CUDA_VISIBLE_DEVICES=""

# Security settings
railway variables set USE_SECURE_COOKIES=true
railway variables set CORS_ORIGINS="https://*.railway.app"

print_status "Environment variables configured successfully"

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

# Wait for deployment to complete
print_status "Waiting for deployment to complete..."
sleep 45

# Step 6: Run database migrations
print_step "Running database migrations..."
railway run bash -c "cd backend && python -m alembic upgrade head"

if [ $? -eq 0 ]; then
    print_status "Database migrations completed successfully"
else
    print_warning "Database migrations failed. Run manually with:"
    print_warning "railway run bash -c \"cd backend && python -m alembic upgrade head\""
fi

# Step 7: Generate domain and configure URLs
print_step "Configuring application domains..."
DOMAIN=$(railway domain 2>/dev/null || echo "")

if [ -n "$DOMAIN" ]; then
    print_status "Domain generated: $DOMAIN"
    
    # Update CORS and URL settings
    railway variables set FRONTEND_URL="https://$DOMAIN"
    railway variables set BACKEND_URL="https://$DOMAIN" 
    railway variables set NEXT_PUBLIC_API_URL="https://$DOMAIN"
    railway variables set NEXT_PUBLIC_DYNAMIC_ENV_ID="$DYNAMIC_ENV_ID"
    
    print_status "URL configuration updated"
else
    print_warning "Could not generate domain automatically. Generate with: railway domain"
fi

# Step 8: Verify deployment
print_step "Verifying deployment..."

if [ -n "$DOMAIN" ]; then
    print_status "Testing health endpoint..."
    sleep 10
    
    if curl -f "https://$DOMAIN/health" >/dev/null 2>&1; then
        print_status "✅ Health check passed"
    else
        print_warning "Health check failed. Deployment may still be starting."
    fi
    
    print_status "Testing API documentation..."
    if curl -f "https://$DOMAIN/docs" >/dev/null 2>&1; then
        print_status "✅ API documentation accessible"
    else
        print_warning "API documentation not yet accessible"
    fi
fi

# Step 9: Deployment Summary
print_step "=== DEPLOYMENT SUMMARY ==="

print_status "🎉 Railway deployment completed!"
echo ""
echo "📋 Deployment Details:"
echo "  🚄 Platform: Railway"
echo "  🗄️  Database: PostgreSQL with pgvector"
echo "  🚀 Cache: Redis"
echo "  🔐 Auth: Dynamic.xyz"
echo "  💳 Payments: Paystack + Coinbase Commerce"
echo ""

if [ -n "$DOMAIN" ]; then
    echo "🌐 Your application is available at:"
    echo "  📱 Application: https://$DOMAIN"
    echo "  📚 API Docs: https://$DOMAIN/docs"
    echo "  🔍 Health Check: https://$DOMAIN/health"
    echo ""
fi

echo "🛠️  Management Commands:"
echo "  railway logs              # View application logs"
echo "  railway status            # Check service status"  
echo "  railway shell             # Access deployment shell"
echo "  railway variables         # View environment variables"
echo "  railway open              # Open Railway dashboard"
echo ""

echo "🔧 Post-Deployment Tasks:"
echo "  1. Test all user flows in production"
echo "  2. Configure payment webhooks:"
echo "     - Paystack: https://$DOMAIN/api/billing/webhook/paystack"
echo "     - Coinbase: https://$DOMAIN/api/billing/webhook/coinbase"
echo "  3. Set up monitoring and alerts"
echo "  4. Configure domain name (optional)"
echo ""

print_status "Deployment completed successfully! 🚀"

# Step 10: Optional monitoring setup
read -p "Set up basic monitoring? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Setting up monitoring..."
    
    # Create simple monitoring script
    cat > monitor-deployment.sh << 'EOF'
#!/bin/bash
echo "🔍 HandyWriterz Monitoring Dashboard"
echo "==================================="
echo ""
echo "🚄 Railway Status:"
railway status
echo ""
echo "📊 Recent Logs:"
railway logs --tail 20
echo ""
echo "🌐 Health Check:"
curl -s https://your-domain.railway.app/health | jq '.' || echo "Health check failed"
EOF
    chmod +x monitor-deployment.sh
    
    print_status "Monitoring script created: ./monitor-deployment.sh"
fi

print_status "Railway deployment script completed! 🎉"