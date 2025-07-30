# Railway Deployment Guide for MultiAgent HandyWriterz

This guide will help you deploy your multi-agent system to Railway with PostgreSQL and Redis support.

## Prerequisites

1. Railway account (sign up at [railway.app](https://railway.app))
2. Railway CLI installed: `npm install -g @railway/cli`
3. Your API keys ready (OpenAI, Anthropic, Gemini, Perplexity)

## Step 1: Railway Setup

### 1.1 Login to Railway
```bash
railway login
```

### 1.2 Create New Project
```bash
railway new
# Choose "Empty Project"
# Name it "multiagent-handywriterz"
```

### 1.3 Link to Existing Project (if you have one)
```bash
railway link
```

## Step 2: Database Setup

### 2.1 Add PostgreSQL
```bash
railway add postgresql
```

This automatically:
- Creates a PostgreSQL database
- Sets `DATABASE_URL` environment variable
- Provides connection details as env vars

### 2.2 Add Redis
```bash
railway add redis
```

This automatically:
- Creates a Redis instance
- Sets `REDIS_URL` environment variable
- Provides Redis connection details

### 2.3 Enable pgvector Extension
```bash
railway run psql $DATABASE_URL -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

## Step 3: Environment Variables

### 3.1 Copy Environment Template
```bash
cp .env.railway .env
```

### 3.2 Set Required Variables
```bash
# Core API Keys (REQUIRED)
railway variables set OPENAI_API_KEY=your_openai_key_here
railway variables set ANTHROPIC_API_KEY=your_anthropic_key_here
railway variables set GEMINI_API_KEY=your_gemini_key_here
railway variables set PERPLEXITY_API_KEY=your_perplexity_key_here

# Security (Generate secure random strings)
railway variables set JWT_SECRET=$(openssl rand -base64 32)
railway variables set ENCRYPTION_KEY=$(openssl rand -base64 32)
railway variables set SESSION_SECRET=$(openssl rand -base64 32)

# Application Settings
railway variables set NODE_ENV=production
railway variables set LOG_LEVEL=info
railway variables set ENABLE_DEBUG_LOGGING=false

# CPU Optimization
railway variables set TORCH_CPU_ONLY=true
railway variables set OMP_NUM_THREADS=2
railway variables set MKL_NUM_THREADS=2
railway variables set CUDA_VISIBLE_DEVICES=""
```

### 3.3 Set Application URLs (After First Deploy)
```bash
# Update these after you get your Railway URLs
railway variables set NEXT_PUBLIC_BACKEND_URL=https://your-service.railway.app
railway variables set BACKEND_URL=https://your-service.railway.app
railway variables set CORS_ALLOW_ORIGIN=https://your-frontend.railway.app
```

## Step 4: Deploy Backend

### 4.1 Deploy Main Service
```bash
railway up
```

Railway will:
- Use `Dockerfile.railway` for building
- Install CPU-optimized dependencies
- Connect to PostgreSQL and Redis automatically
- Deploy with 2 workers for efficiency

### 4.2 Run Database Migrations
```bash
railway run python -m alembic upgrade head
```

## Step 5: Deploy Frontend (Separate Service)

### 5.1 Create Frontend Service
```bash
railway service create frontend
railway service link frontend
```

### 5.2 Deploy Frontend
```bash
cd frontend/web/HandyWriterz
railway up
```

## Step 6: Deploy Celery Workers (Optional)

### 6.1 Create Worker Service
```bash
railway service create celery-worker
railway service link celery-worker
```

### 6.2 Set Worker Command
```bash
railway variables set --service celery-worker START_COMMAND="celery -A src.workers.celery_app worker --loglevel=info --concurrency=2"
```

### 6.3 Deploy Worker
```bash
railway up --service celery-worker
```

## Step 7: Configure Domain & HTTPS

### 7.1 Generate Domain
```bash
railway domain
```

### 7.2 Custom Domain (Optional)
```bash
railway domain add yourdomain.com
```

Railway automatically provides:
- HTTPS certificates
- Load balancing
- Auto-scaling

## Step 8: Monitor & Scale

### 8.1 View Logs
```bash
railway logs
```

### 8.2 View Metrics
```bash
railway status
```

### 8.3 Scale Services
```bash
# Scale backend replicas
railway variables set RAILWAY_REPLICA_COUNT=2

# Scale worker resources
railway variables set --service celery-worker RAILWAY_MEMORY_LIMIT=1024
```

## Architecture Overview

```
Internet
    ↓
Railway Load Balancer (HTTPS)
    ↓
┌──────────────┬─────────────────┬─────────────────┐
│   Frontend   │   Backend API   │  Celery Worker  │
│   (Next.js)  │   (FastAPI)     │   (Background)  │
│   Port 3000  │   Port 8000     │   Redis Queue   │
└──────────────┴─────────────────┴─────────────────┘
        │                │               │
        └────────────────┼───────────────┘
                         ↓
           ┌─────────────────────────────┐
           │     Railway Services        │
           │ ┌─────────┬───────────────┐ │
           │ │PostgreSQL│     Redis     │ │
           │ │(pgvector)│   (Celery)    │ │
           │ └─────────┴───────────────┘ │
           └─────────────────────────────┘
```

## Resource Limits (Free Tier)

- **Execution Time**: 500 hours/month
- **Memory**: Up to 8GB per service
- **CPU**: Shared vCPU
- **Storage**: 100GB total
- **Bandwidth**: Unlimited

## Cost Optimization

1. **Use CPU-only models** (already configured)
2. **Efficient workers**: 2 workers instead of 4
3. **Sleep unused services**: Frontend can sleep during low traffic
4. **Optimize Docker layers**: Multi-stage builds reduce image size
5. **Monitor usage**: Use Railway dashboard to track resource usage

## Troubleshooting

### Common Issues

1. **Database connection errors**
   ```bash
   railway run python -c "import os; print(os.getenv('DATABASE_URL'))"
   ```

2. **Redis connection errors**
   ```bash
   railway run python -c "import os; print(os.getenv('REDIS_URL'))"
   ```

3. **Build failures**
   ```bash
   railway logs --build
   ```

4. **Memory issues**
   ```bash
   railway variables set RAILWAY_MEMORY_LIMIT=1024
   ```

### Debug Commands

```bash
# Check all environment variables
railway variables

# Connect to database
railway run psql $DATABASE_URL

# Connect to Redis
railway run redis-cli --url $REDIS_URL

# Shell access
railway shell
```

## Production Checklist

- [ ] All API keys configured
- [ ] Database migrations applied
- [ ] Redis connection working
- [ ] Frontend-backend communication working
- [ ] File uploads working
- [ ] WebSocket connections working
- [ ] Multi-agent responses generating
- [ ] Background tasks processing
- [ ] Error monitoring setup
- [ ] Domain configured
- [ ] HTTPS working

## Next Steps

1. **Monitor Performance**: Use Railway metrics dashboard
2. **Set up Alerts**: Configure email notifications for errors
3. **Backup Database**: Set up automated PostgreSQL backups
4. **CDN Setup**: Use Railway's built-in CDN for static assets
5. **Scale as Needed**: Upgrade to paid tier when you exceed free limits

Your multi-agent system is now ready for production on Railway! 🚀