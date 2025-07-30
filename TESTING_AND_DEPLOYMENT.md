# HandyWriterz Testing & Deployment Guide

Complete guide for testing all user flows and deploying to Railway with Docker.

## 🐳 Docker Testing

### Prerequisites
- Docker 28.3.0+ installed
- Docker Desktop running (or Docker daemon)
- 8GB+ RAM available for Docker

### Quick Start - Run All Tests

```bash
# Run comprehensive Docker-based tests
./scripts/docker-test.sh
```

This will:
1. 🏗️ Build all Docker images (backend, frontend, test runner)
2. 🗄️ Start PostgreSQL with pgvector extension
3. 🚀 Start Redis cache
4. 🔧 Start backend API server
5. ⚛️ Start frontend Next.js server
6. 🧪 Run comprehensive test suite
7. 📊 Generate test report

### Manual Testing Steps

```bash
# 1. Start test infrastructure
docker-compose -f docker-compose.test.yml up -d postgres-test redis-test

# 2. Wait for services
./scripts/wait-for-services.sh

# 3. Start application services
docker-compose -f docker-compose.test.yml up -d backend-test frontend-test

# 4. Run specific test suites
docker-compose -f docker-compose.test.yml run --rm test-runner
```

### Test Access URLs (when running)
- **Frontend**: http://localhost:3001
- **Backend**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs

## 🧪 Test Coverage

### 1. Infrastructure Tests
- ✅ PostgreSQL connection and pgvector extension
- ✅ Redis connectivity
- ✅ Database migrations
- ✅ Health endpoints

### 2. Authentication Tests
- ✅ Dynamic.xyz wallet connection
- ✅ MPC wallet assignment
- ✅ JWT token validation
- ✅ User creation and retrieval

### 3. Payment Flow Tests
- ✅ **Paystack Integration**:
  - Payment link generation
  - Webhook signature verification
  - Subscription activation
- ✅ **Coinbase Commerce Integration**:
  - Crypto charge creation
  - Payment confirmation
  - USDC processing

### 4. User Interface Tests
- ✅ Homepage and navigation
- ✅ Chat interface functionality
- ✅ File upload and processing
- ✅ Settings and billing pages
- ✅ Theme toggle (light/dark/system)
- ✅ Responsive design (mobile/desktop)

### 5. AI Agent Tests
- ✅ LangGraph configuration
- ✅ Agent node imports
- ✅ State management
- ✅ Real AI API integration (Gemini, Perplexity)

### 6. End-to-End User Journeys
- ✅ **New User Flow**:
  1. Connect wallet via Dynamic.xyz
  2. MPC wallet automatically assigned
  3. Access chat interface
  4. Upload documents
  5. Generate AI content
- ✅ **Payment Flow**:
  1. View pricing tiers
  2. Select subscription plan
  3. Choose payment method (card/crypto)
  4. Complete payment
  5. Verify upgrade
- ✅ **Content Creation Flow**:
  1. Upload PDF/DOCX files
  2. Select writing tool
  3. Generate academic content
  4. Export in multiple formats

## 🚄 Railway Deployment

### Prerequisites
- Railway CLI installed: `npm install -g @railway/cli`
- Railway account: https://railway.app
- API keys for all services

### Quick Deployment

```bash
# Deploy to Railway
./scripts/railway-deploy.sh
```

### Manual Deployment Steps

```bash
# 1. Login to Railway
railway login

# 2. Create/link project
railway new handywriterz-ai
# OR
railway link

# 3. Add services
railway add postgresql
railway add redis

# 4. Set environment variables
railway variables set OPENAI_API_KEY="your_key"
railway variables set ANTHROPIC_API_KEY="your_key"
railway variables set GEMINI_API_KEY="your_key"
railway variables set PERPLEXITY_API_KEY="your_key"
railway variables set PAYSTACK_SECRET_KEY="your_key"
railway variables set COINBASE_API_KEY="your_key"
railway variables set DYNAMIC_ENV_ID="your_env_id"
railway variables set DYNAMIC_PUBLIC_KEY="your_public_key"

# 5. Deploy application
railway up

# 6. Run migrations
railway run bash -c "cd backend && python -m alembic upgrade head"

# 7. Generate domain
railway domain
```

## 🔐 Required Environment Variables

### AI Providers
```bash
OPENAI_API_KEY=sk-...                    # OpenAI GPT models
ANTHROPIC_API_KEY=sk-ant-...             # Claude models  
GEMINI_API_KEY=AIza...                   # Google Gemini
PERPLEXITY_API_KEY=pplx-...              # Perplexity AI
```

### Payment Providers
```bash
PAYSTACK_SECRET_KEY=sk_live_...          # Paystack payments
PAYSTACK_PUBLIC_KEY=pk_live_...          # Paystack public key
COINBASE_API_KEY=...                     # Coinbase Commerce
COINBASE_WEBHOOK_SECRET=...              # Webhook verification
```

### Authentication
```bash
DYNAMIC_ENV_ID=...                       # Dynamic.xyz environment
DYNAMIC_PUBLIC_KEY=...                   # Dynamic.xyz public key
JWT_SECRET_KEY=...                       # JWT signing secret
```

### Database (Railway provides these)
```bash
DATABASE_URL=postgresql://...            # PostgreSQL connection
REDIS_URL=redis://...                    # Redis connection
```

## 🧪 Test Commands Reference

### Docker Tests
```bash
# Full test suite
./scripts/docker-test.sh

# Backend tests only
docker-compose -f docker-compose.test.yml run --rm backend-test uv run pytest

# Frontend tests only
docker-compose -f docker-compose.test.yml run --rm frontend-test pnpm test

# E2E tests only
docker-compose -f docker-compose.test.yml run --rm frontend-test npx playwright test

# Clean up
docker-compose -f docker-compose.test.yml down --volumes
```

### Individual Test Suites
```bash
# Backend unit tests
cd backend && uv run pytest src/tests/ -v

# Backend E2E tests
cd backend && uv run pytest src/tests/e2e/ -v

# Frontend component tests
cd frontend && pnpm test

# Playwright E2E tests
cd frontend && npx playwright test

# API integration tests
cd frontend && npx playwright test --grep "API Integration"
```

## 🔍 Monitoring & Debugging

### Railway Monitoring
```bash
# View logs
railway logs

# Check service status
railway status

# Access deployment shell
railway shell

# View environment variables
railway variables
```

### Local Debugging
```bash
# View Docker container logs
docker-compose -f docker-compose.test.yml logs backend-test
docker-compose -f docker-compose.test.yml logs frontend-test

# Access container shell
docker-compose -f docker-compose.test.yml exec backend-test bash
docker-compose -f docker-compose.test.yml exec frontend-test sh

# Monitor resource usage
docker stats
```

## 🚨 Troubleshooting

### Common Issues

#### Docker Out of Memory
```bash
# Increase Docker memory limit to 8GB+
# In Docker Desktop: Settings > Resources > Memory
```

#### Tests Timeout
```bash
# Increase timeout in test configuration
# Check Docker container resources
docker stats

# Restart Docker daemon
sudo systemctl restart docker
```

#### Database Connection Failed
```bash
# Check PostgreSQL is running
docker-compose -f docker-compose.test.yml logs postgres-test

# Verify connection string
docker-compose -f docker-compose.test.yml exec postgres-test pg_isready -U handywriterz
```

#### Railway Deployment Failed
```bash
# Check build logs
railway logs

# Verify environment variables
railway variables

# Check service status
railway status
```

## ✅ Pre-Deployment Checklist

### Development Testing
- [ ] All Docker tests pass: `./scripts/docker-test.sh`
- [ ] Backend E2E tests pass: `cd backend && uv run pytest src/tests/e2e/`
- [ ] Frontend E2E tests pass: `cd frontend && npx playwright test`
- [ ] Payment flows tested (sandbox)
- [ ] Authentication flows tested
- [ ] File upload/processing tested

### Production Setup
- [ ] All API keys configured
- [ ] Payment webhooks configured
- [ ] Domain name configured (optional)
- [ ] Monitoring set up
- [ ] Backup strategy implemented

### Post-Deployment Verification
- [ ] Health endpoints responding
- [ ] Database connections working
- [ ] Payment integration functional
- [ ] AI agents operational
- [ ] Frontend loading correctly

## 📊 Performance Benchmarks

Expected performance metrics:
- **Backend startup**: < 30 seconds
- **Frontend build**: < 5 minutes
- **API response time**: < 500ms (health endpoint)
- **Database queries**: < 100ms average
- **Payment processing**: < 10 seconds
- **AI content generation**: 30-120 seconds

## 🎯 Success Criteria

Deployment is successful when:
1. ✅ All tests pass in Docker environment
2. ✅ Railway deployment completes without errors
3. ✅ Health endpoints return 200 OK
4. ✅ Payment flows work end-to-end
5. ✅ Authentication system functional
6. ✅ AI content generation working
7. ✅ Frontend UI responsive and functional

---

**Next Steps**: Run `./scripts/docker-test.sh` to verify everything works, then `./scripts/railway-deploy.sh` to deploy to production!