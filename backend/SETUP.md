# HandyWriterz Backend Setup Guide

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd handywriterz/backend/backend

# Run the automated setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and configuration

# Start the development server
./scripts/run_dev.sh
```

## 📋 Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **PostgreSQL**: 14 or higher (with pgvector extension)
- **Redis**: 6.0 or higher
- **Node.js**: 18 or higher (for frontend)
- **Git**: Latest version

### Required API Keys
- **Anthropic API Key**: For Claude 3.5 Sonnet
- **OpenAI API Key**: For GPT-4o
- **Google Gemini API Key**: For Gemini 1.5 Pro
- **Perplexity API Key**: For research capabilities

## 🛠️ Manual Setup

### 1. Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install dependencies
pip install -r requirements.txt
```

### 2. PostgreSQL Setup

```bash
# Install PostgreSQL (if not installed)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Windows:
# Download from https://www.postgresql.org/download/windows/

# Start PostgreSQL service
# Linux:
sudo systemctl start postgresql
# macOS:
brew services start postgresql

# Create database and user
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE USER handywriterz WITH PASSWORD 'handywriterz_dev_2024';
CREATE DATABASE handywriterz OWNER handywriterz;
GRANT ALL PRIVILEGES ON DATABASE handywriterz TO handywriterz;

# Install pgvector extension
\c handywriterz
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

### 3. Redis Setup

```bash
# Install Redis
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Windows:
# Download from https://github.com/microsoftarchive/redis/releases

# Start Redis
redis-server --daemonize yes

# Test Redis connection
redis-cli ping
# Should return: PONG
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configuration
# Required configurations:
# - AI Provider API keys
# - Database connection string
# - JWT secret key
# - Dynamic.xyz credentials (for authentication)
```

### 5. Database Migrations

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Update alembic.ini with your database URL
# Edit line: sqlalchemy.url = postgresql://handywriterz:password@localhost/handywriterz

# Generate initial migration
alembic revision --autogenerate -m "Initial migration"

# Run migrations
alembic upgrade head
```

### 6. Seed Data (Optional)

```bash
# Create test data for development
python scripts/seed_data.py
```

## 🔧 Configuration Details

### Environment Variables

#### Critical Variables (Must Set)
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secure key for JWT tokens (min 32 chars)
- `ANTHROPIC_API_KEY`: Primary AI provider
- `REDIS_URL`: Redis connection string

#### Production Variables
- `ENVIRONMENT`: Set to "production"
- `DEBUG`: Set to "false"
- `SENTRY_DSN`: For error tracking
- `R2_*` or `AWS_*`: Cloud storage configuration

### Database Schema

The application uses the following main tables:
- `users`: User accounts and profiles
- `conversations`: Writing workflow sessions
- `documents`: Generated academic documents
- `user_fingerprints`: Writing style analysis
- `source_cache`: Cached research sources
- `system_metrics`: Performance monitoring

### API Endpoints

After starting the server, you can access:
- API Documentation: http://localhost:8000/docs
- Alternative API Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## 🚀 Running the Application

### Development Mode

```bash
# Using the run script
./scripts/run_dev.sh

# Or manually
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Using the run script
./scripts/run_prod.sh

# Or with gunicorn
cd src
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Running with Docker

```bash
# Build the image
docker build -t handywriterz-backend .

# Run the container
docker run -p 8000:8000 --env-file .env handywriterz-backend
```

## 🧪 Testing

```bash
# Run all tests
./scripts/test.sh

# Or manually
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src --cov-report=html

# Run specific test file
pytest tests/test_agents.py -v

# Run with markers
pytest -m "not slow" -v
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: could not connect to database
```
**Solution**: 
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify DATABASE_URL in .env
- Check user permissions: `psql -U handywriterz -d handywriterz`

#### 2. Redis Connection Error
```
Error: Redis connection refused
```
**Solution**:
- Check Redis is running: `redis-cli ping`
- Start Redis: `redis-server --daemonize yes`
- Verify REDIS_URL in .env

#### 3. Missing API Keys
```
Error: ANTHROPIC_API_KEY not set
```
**Solution**:
- Add all required API keys to .env
- Ensure .env file is in the correct directory
- Check environment variable names match exactly

#### 4. Import Errors
```
ModuleNotFoundError: No module named 'xxx'
```
**Solution**:
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.10+)

#### 5. Alembic Migration Errors
```
Error: Target database is not up to date
```
**Solution**:
- Run migrations: `alembic upgrade head`
- Check current version: `alembic current`
- Reset if needed: `alembic downgrade base && alembic upgrade head`

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
export DEBUG=true
./scripts/run_dev.sh
```

### Health Checks

Check system health:
```bash
# API health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health/db

# Redis health
curl http://localhost:8000/health/redis
```

## 📚 Additional Resources

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [Architecture Overview](../../../Claude.md)
- [Development Roadmap](../../../todo2.md)

### External Documentation
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [LangGraph](https://python.langchain.com/docs/langgraph)

### Support
- GitHub Issues: [Create an issue](https://github.com/your-repo/issues)
- Discord: [Join our community](https://discord.gg/your-invite)
- Email: support@handywriterz.com

## 🔒 Security Considerations

1. **Never commit .env files** to version control
2. **Use strong JWT secret keys** (minimum 64 characters for production)
3. **Rotate API keys regularly**
4. **Enable rate limiting** in production
5. **Use HTTPS** for all production deployments
6. **Keep dependencies updated**: `pip list --outdated`

## 🎯 Next Steps

1. Complete environment configuration in .env
2. Run the test suite to verify setup
3. Access API documentation at /docs
4. Start implementing agents (see todo2.md)
5. Set up monitoring and logging for production

---

For questions or issues, please refer to the troubleshooting section or create a GitHub issue.