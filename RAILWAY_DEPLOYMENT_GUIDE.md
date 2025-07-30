# 🚄 Railway CLI Deployment Guide

## Ready to Deploy HandyWriterz to Railway

Your application has passed all 29 verification tests and is ready for production deployment to Railway.

## 🔑 Prerequisites

You'll need the following API keys before starting:

### AI Providers (at least one required)
- **OpenAI API Key**: `sk-...` from https://platform.openai.com/api-keys
- **Anthropic API Key**: `sk-ant-...` from https://console.anthropic.com/
- **Gemini API Key**: `AIza...` from https://aistudio.google.com/app/apikey
- **Perplexity API Key**: `pplx-...` from https://www.perplexity.ai/settings/api

### Payment Providers (both required)
- **Paystack Secret Key**: `sk_live_...` from https://dashboard.paystack.com/settings/developer
- **Coinbase Commerce API Key**: From https://commerce.coinbase.com/dashboard/api-keys

### Authentication (required)
- **Dynamic.xyz Environment ID**: From https://app.dynamic.xyz/dashboard/developer
- **Dynamic.xyz Public Key**: From your Dynamic.xyz dashboard

## 🚀 Step-by-Step Deployment

### 1. Authenticate with Railway

```bash
railway login
```
This will open your browser to authenticate with GitHub/Google/Discord.

### 2. Create Railway Project

```bash
railway new handywriterz-ai
```
Or link to existing project:
```bash
railway link
```

### 3. Add Required Services

```bash
# Add PostgreSQL database
railway add postgresql

# Add Redis cache
railway add redis
```

### 4. Enable pgvector Extension

```bash
# Wait for PostgreSQL to be ready (2-3 minutes)
railway run psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### 5. Set Environment Variables

Use the automated script:
```bash
./scripts/railway-deploy.sh
```

Or set manually:
```bash
# AI Provider Keys
railway variables set OPENAI_API_KEY="your_openai_key"
railway variables set ANTHROPIC_API_KEY="your_anthropic_key"
railway variables set GEMINI_API_KEY="your_gemini_key"
railway variables set PERPLEXITY_API_KEY="your_perplexity_key"

# Payment Provider Keys
railway variables set PAYSTACK_SECRET_KEY="your_paystack_key"
railway variables set COINBASE_API_KEY="your_coinbase_key"

# Dynamic.xyz Auth
railway variables set DYNAMIC_ENV_ID="your_dynamic_env_id"
railway variables set DYNAMIC_PUBLIC_KEY="your_dynamic_public_key"

# Application Configuration
railway variables set ENVIRONMENT="production"
railway variables set NODE_ENV="production"
railway variables set LOG_LEVEL="INFO"

# Generate secure JWT secret
railway variables set JWT_SECRET_KEY="$(openssl rand -base64 32)"

# Performance optimizations
railway variables set TORCH_CPU_ONLY="true"
railway variables set OMP_NUM_THREADS="2"
railway variables set MKL_NUM_THREADS="2"
```

### 6. Deploy Application

```bash
railway up --detach
```

This will:
- Build your Docker containers
- Deploy backend and frontend services
- Start the application with health checks

### 7. Run Database Migrations

```bash
railway run bash -c "cd backend && python -m alembic upgrade head"
```

### 8. Generate Domain

```bash
railway domain
```

This creates a public URL like: `https://handywriterz-ai-production.up.railway.app`

### 9. Update URL Configuration

```bash
DOMAIN=$(railway domain show)
railway variables set FRONTEND_URL="https://$DOMAIN"
railway variables set BACKEND_URL="https://$DOMAIN"
railway variables set NEXT_PUBLIC_API_URL="https://$DOMAIN"
```

### 10. Verify Deployment

```bash
# Check health endpoint
curl https://your-domain.railway.app/health

# View API documentation
curl https://your-domain.railway.app/docs

# Check application logs
railway logs

# View service status
railway status
```

## 🔧 Post-Deployment Configuration

### Configure Payment Webhooks

Add these webhook URLs to your payment providers:

**Paystack Dashboard** → Settings → Webhooks:
```
https://your-domain.railway.app/api/billing/webhook/paystack
```

**Coinbase Commerce Dashboard** → Settings → Webhook subscriptions:
```
https://your-domain.railway.app/api/billing/webhook/coinbase
```

### Test Payment Flows

1. Visit your application
2. Connect wallet via Dynamic.xyz
3. Try upgrading to a paid plan
4. Test both Paystack and Coinbase payment methods

## 📊 Monitoring & Management

### Essential Railway Commands

```bash
# View real-time logs
railway logs --tail

# Check service status
railway status

# Access deployment shell
railway shell

# View all environment variables
railway variables

# Open Railway dashboard
railway open

# Redeploy application
railway up

# Scale services (if needed)
railway scale backend replicas=2
```

### Health Monitoring

Your application includes these health endpoints:
- **Health Check**: `/health` - Basic service status
- **API Documentation**: `/docs` - Interactive API docs
- **Metrics**: `/metrics` - Performance metrics (if configured)

## 🚨 Troubleshooting

### Common Issues

**Build Fails**:
```bash
# Check build logs
railway logs --service backend

# Try rebuilding
railway up --force
```

**Database Connection Issues**:
```bash
# Test database connection
railway run psql $DATABASE_URL -c "SELECT 1;"

# Check if pgvector is installed
railway run psql $DATABASE_URL -c "SELECT * FROM pg_extension WHERE extname='vector';"
```

**Environment Variables Missing**:
```bash
# List all variables
railway variables

# Add missing variable
railway variables set VARIABLE_NAME="value"
```

**Application Not Starting**:
```bash
# Check application logs
railway logs --tail 100

# Restart services
railway restart
```

## 🎯 Success Checklist

- [ ] Railway CLI authenticated
- [ ] Project created with PostgreSQL and Redis
- [ ] All environment variables set
- [ ] Application deployed successfully
- [ ] Database migrations completed
- [ ] Domain generated and accessible
- [ ] Health endpoints responding
- [ ] Payment webhooks configured
- [ ] User flows tested in production

## 🎉 Deployment Complete!

Once deployed, your HandyWriterz application will be available at:

- **Application**: https://your-domain.railway.app
- **API Docs**: https://your-domain.railway.app/docs
- **Health Check**: https://your-domain.railway.app/health

The application includes:
- ✅ Web3 authentication with automatic MPC wallet creation
- ✅ Dual payment processing (Paystack + Coinbase Commerce)
- ✅ AI-powered content generation with real-time streaming
- ✅ File upload and vector search capabilities
- ✅ Multi-format export (PDF, DOCX, PowerPoint)
- ✅ Production-ready monitoring and error handling

**Your AI-powered academic writing platform is now live! 🚀**