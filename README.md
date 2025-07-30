# 🚀 HandyWriterz - Revolutionary AI-Powered Academic Writing Platform

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Railway](https://img.shields.io/badge/Deploy-Railway-blueviolet.svg)](https://railway.app)

> **Transform research materials into publication-ready academic content using 30+ specialized AI agents working in intelligent swarms.**

## 📖 Table of Contents

- [🌟 Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [📋 Requirements](#-requirements)
- [🛠️ Installation](#️-installation)
- [⚙️ Configuration](#️-configuration)
- [🚢 Deployment](#-deployment)
- [📖 Usage](#-usage)
- [🔌 API Documentation](#-api-documentation)
- [🧪 Testing](#-testing)
- [🔧 Development](#-development)
- [💼 Business Model](#-business-model)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🌟 Overview

HandyWriterz is a cutting-edge AI-powered academic writing platform that revolutionizes how students, researchers, and academics create scholarly content. By leveraging a sophisticated multi-agent system with 30+ specialized AI agents, the platform transforms raw research materials into polished, citation-ready academic papers.

### 🎯 **What Makes HandyWriterz Different?**

- **Multi-Agent Intelligence**: 30+ specialized agents working collaboratively in orchestrated swarms
- **Academic Focus**: Purpose-built for scholarly writing with proper citation management
- **Multimodal Processing**: Handles PDF, DOCX, audio, video, and image files
- **Real-time Streaming**: Live workflow visualization with progress tracking
- **Quality Assurance**: Multi-layer validation and plagiarism detection
- **Production Ready**: CPU-optimized, scalable architecture for enterprise deployment

### 🎓 **Target Users**

- **Students**: Undergraduate to PhD level academic writing assistance
- **Researchers**: Literature reviews, research papers, grant proposals
- **Academics**: Publication-ready content with proper citations
- **Institutions**: Bulk academic writing and research support
- **Professionals**: Business reports, white papers, market research

## ✨ Key Features

### 🤖 **Multi-Agent System Architecture**

#### **Research Swarm**
- **ArXiv Specialist**: Advanced scientific paper analysis
- **Cross-Disciplinary Researcher**: Multi-domain knowledge synthesis
- **Methodology Expert**: Research design and statistical analysis
- **Scholar Network**: Academic citation and collaboration tracking
- **Trend Analysis**: Emerging research patterns identification

#### **Writing Swarm**
- **Academic Tone Optimizer**: Scholarly language enhancement
- **Clarity Enhancer**: Readability and comprehension improvement
- **Structure Optimizer**: Logical flow and organization
- **Style Adaptation**: Formatting for different academic styles
- **Citation Master**: Proper referencing and bibliography management

#### **QA Swarm**
- **Argument Validation**: Logical consistency checking
- **Bias Detection**: Unconscious bias identification and correction
- **Fact-Checking**: Source verification and accuracy validation
- **Ethical Reasoning**: Research ethics compliance
- **Originality Guard**: Plagiarism prevention and uniqueness scoring

### 📚 **Comprehensive Academic Support**

#### **Document Types**
- Essays and Research Papers
- Dissertations and Theses
- Literature Reviews
- Case Studies and Reports
- Grant Proposals
- Conference Papers

#### **Citation Styles**
- Harvard, APA, MLA, Chicago
- Vancouver, IEEE, Nature
- Custom institutional styles

#### **Academic Levels**
- Undergraduate (Bachelor's)
- Graduate (Master's)
- Doctoral (PhD, DPhil)
- Postdoctoral Research

#### **Regional Standards**
- UK Academic Standards
- US University Requirements
- Australian Education System
- Canadian Institutions
- European Academic Conventions

### 🔄 **Intelligent Processing Pipeline**

```mermaid
graph TD
    A[File Upload] --> B[Intent Analysis]
    B --> C[Planning Phase]
    C --> D[Research Swarm]
    D --> E[Source Verification]
    E --> F[Writing Swarm]
    F --> G[QA Swarm]
    G --> H[Citation Management]
    H --> I[Plagiarism Check]
    I --> J[Format & Deliver]
```

### 📁 **Multimodal File Processing**

#### **Supported Formats**
- **Documents**: PDF, DOCX, TXT, MD, RTF
- **Audio**: MP3, WAV, OGG (Whisper transcription)
- **Video**: MP4, WebM, AVI (content extraction)
- **Images**: JPG, PNG, GIF, WebP (OCR and analysis)
- **Data**: CSV, XLSX (statistical analysis)

#### **Processing Capabilities**
- **Smart Chunking**: Citation-aware document splitting
- **Vector Embeddings**: Semantic search with pgvector
- **Content Extraction**: Text, metadata, and structure analysis
- **File Limits**: Up to 50 files, 100MB each, 500MB total

## 🏗️ Architecture

### **System Overview**

HandyWriterz implements a modern, scalable architecture designed for high-performance academic content generation:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   AI Models     │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Multi-LLM)   │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   File Storage  │    │   PostgreSQL    │    │   Redis Cache   │
│   (Cloudflare)  │    │   + pgvector    │    │   + Sessions    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Technology Stack**

#### **Backend**
- **Framework**: FastAPI 0.116.1 with Pydantic models
- **AI Orchestration**: LangGraph for multi-agent coordination
- **Database**: PostgreSQL 15+ with pgvector extension
- **Caching**: Redis 7.0+ for session management and SSE streaming
- **Authentication**: JWT-based with Dynamic.xyz Web3 integration
- **File Processing**: Async upload handling with TUS protocol
- **Security**: Rate limiting, CORS, input validation, CSRF protection

#### **Frontend**
- **Framework**: Next.js 14 with React 19 and TypeScript
- **UI Components**: Shadcn/ui with Radix UI primitives
- **Styling**: Tailwind CSS with responsive design
- **State Management**: Zustand for client state
- **File Upload**: TUS resumable uploads with progress tracking
- **Real-time**: WebSocket integration for live updates

#### **AI Models**
- **Primary Writer**: Gemini 2.5 Pro
- **Advanced Search**: OpenAI O3 Reasoner, Sonar Deep, Kimi K2
- **Quality Assurance**: Claude Opus for evaluation
- **Specialized Tasks**: DeepSeek, Qwen, Grok for specific domains

#### **Infrastructure**
- **Deployment**: Docker containers with Railway/AWS deployment
- **Monitoring**: Health checks, metrics collection, error tracking  
- **Scaling**: Multi-worker Gunicorn with Uvicorn workers
- **Storage**: Cloudflare R2 for file storage, local filesystem fallback

## 🚀 Quick Start

### **Prerequisites**

- Python 3.11+ with pip
- Node.js 18+ with npm/pnpm
- PostgreSQL 15+ with pgvector
- Redis 7.0+
- Git

### **1. Clone the Repository**

```bash
git clone https://github.com/Abelhubprog/HandyWriterzAi.git
cd HandyWriterzAi
```

### **2. Backend Setup**

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration (see Configuration section)

# Run database migrations
alembic upgrade head

# Start the backend server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### **3. Frontend Setup**

```bash
# Navigate to frontend directory (in new terminal)
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Start the development server
npm run dev
```

### **4. Access the Application**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin

## 📋 Requirements

### **System Requirements**

#### **Minimum (Development)**
- **CPU**: 2 cores, 2.0GHz
- **RAM**: 4GB available memory
- **Storage**: 10GB free disk space
- **Network**: Stable internet connection for AI model APIs

#### **Recommended (Production)**
- **CPU**: 4+ cores, 3.0GHz+
- **RAM**: 8GB+ available memory
- **Storage**: 50GB+ SSD storage
- **Network**: High-speed internet with low latency

### **Software Dependencies**

#### **Backend**
```python
# Core dependencies
fastapi>=0.116.1
uvicorn[standard]>=0.35.0
sqlalchemy>=2.0.0
alembic>=1.16.0
asyncpg>=0.30.0
redis>=5.2.0
pydantic>=2.5.0
python-multipart>=0.0.6

# AI & ML
langchain>=0.3.0
langgraph>=0.2.0
anthropic>=0.58.0
openai>=1.0.0
google-generativeai>=0.8.0

# File Processing
PyPDF2>=3.0.0
python-docx>=1.1.0
python-tus>=1.9.0
pillow>=10.0.0
whisper>=1.0.0
```

#### **Frontend**
```json
{
  "next": "^14.0.0",
  "react": "^19.0.0",
  "react-dom": "^19.0.0",
  "typescript": "^5.0.0",
  "@dynamic-labs/sdk-react-core": "^3.9.0",
  "tailwindcss": "^3.4.0",
  "lucide-react": "^0.400.0",
  "tus-js-client": "^4.0.0",
  "react-dropzone": "^14.0.0"
}
```

## 🛠️ Installation

### **Development Installation**

#### **1. System Dependencies**

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install -y \
    python3.11 python3.11-pip python3.11-venv \
    nodejs npm \
    postgresql-15 postgresql-contrib \
    redis-server \
    git curl build-essential \
    libpq-dev pkg-config libffi-dev
```

**macOS (Homebrew):**
```bash
brew install python@3.11 node postgresql@15 redis git
brew services start postgresql@15
brew services start redis
```

**Windows (Chocolatey):**
```powershell
choco install python311 nodejs postgresql15 redis git
```

#### **2. PostgreSQL Setup**

```bash
# Create database and user
sudo -u postgres psql
```

```sql
CREATE DATABASE handywriterz;
CREATE USER handywriterz_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE handywriterz TO handywriterz_user;

-- Enable pgvector extension
\c handywriterz
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

#### **3. Redis Configuration**

```bash
# Edit Redis configuration (optional)
sudo nano /etc/redis/redis.conf

# Restart Redis
sudo systemctl restart redis-server
```

#### **4. Environment Setup**

**Backend Configuration (.env):**
```bash
# Database
DATABASE_URL=postgresql://handywriterz_user:your_secure_password@localhost:5432/handywriterz
REDIS_URL=redis://localhost:6379/0

# AI Model APIs (Required)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GEMINI_API_KEY=your_gemini_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key

# Security
JWT_SECRET=your_jwt_secret_key_32_chars
ENCRYPTION_KEY=your_encryption_key_32_chars
SESSION_SECRET=your_session_secret_32_chars

# Application
NODE_ENV=development
LOG_LEVEL=info
CORS_ALLOW_ORIGIN=http://localhost:3000

# Optional Services
STRIPE_SECRET_KEY=your_stripe_secret_key
COINBASE_API_KEY=your_coinbase_api_key
TURNITIN_API_KEY=your_turnitin_api_key
```

**Frontend Configuration (.env.local):**
```bash
# API Configuration
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Feature Flags
NEXT_PUBLIC_ENABLE_DOCX_CONVERT=true
NEXT_PUBLIC_ENABLE_UNMUTE=true
NEXT_PUBLIC_ENABLE_MM_RESEARCH=true
NEXT_PUBLIC_ENABLE_SUBSCRIPTION_BILLING=true

# Web3 Configuration
NEXT_PUBLIC_DYNAMIC_ENV_ID=your_dynamic_environment_id

# Pricing
NEXT_PUBLIC_PRICE_PER_PAGE_GBP=12
NEXT_PUBLIC_WORDS_PER_PAGE=275
NEXT_PUBLIC_TRIAL_WORD_LIMIT=1000
```

### **Production Installation**

#### **1. Docker Setup**

**Build and run with Docker Compose:**
```bash
# Development environment
docker-compose -f docker-compose.yml up -d

# Production environment
docker-compose -f docker-compose.prod.yml up -d
```

#### **2. Railway Deployment**

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

#### **3. Environment Variables for Production**

Set these in your deployment platform (Railway, AWS, etc.):

```bash
# Database (Auto-provided by Railway)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Required API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
PERPLEXITY_API_KEY=pplx-...

# Security (Generate 32-character random strings)
JWT_SECRET=...
ENCRYPTION_KEY=...
SESSION_SECRET=...

# Production URLs
NEXT_PUBLIC_APP_URL=https://your-app.railway.app
NEXT_PUBLIC_BACKEND_URL=https://your-api.railway.app
CORS_ALLOW_ORIGIN=https://your-app.railway.app
```

## ⚙️ Configuration

### **Environment Variables Reference**

#### **Database Configuration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Yes | - |
| `REDIS_URL` | Redis connection string | Yes | `redis://localhost:6379/0` |

#### **AI Model Configuration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key for GPT models | Yes | - |
| `ANTHROPIC_API_KEY` | Anthropic API key for Claude | Yes | - |
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| `PERPLEXITY_API_KEY` | Perplexity API key for search | Yes | - |
| `DEEPSEEK_API_KEY` | DeepSeek API key | No | - |
| `QWEN_API_KEY` | Qwen API key | No | - |

#### **Security Configuration**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `JWT_SECRET` | JWT signing secret (32 chars) | Yes | - |
| `ENCRYPTION_KEY` | Data encryption key (32 chars) | Yes | - |
| `SESSION_SECRET` | Session signing secret (32 chars) | Yes | - |
| `CORS_ALLOW_ORIGIN` | Allowed CORS origins | Yes | `*` |

#### **Feature Flags**
| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEXT_PUBLIC_ENABLE_DOCX_CONVERT` | Enable DOCX conversion | No | `true` |
| `NEXT_PUBLIC_ENABLE_SUBSCRIPTION_BILLING` | Enable billing system | No | `false` |
| `NEXT_PUBLIC_ENABLE_ANALYTICS` | Enable analytics tracking | No | `false` |

### **Model Configuration**

The platform supports dynamic model configuration through the admin interface. Default model assignments:

```yaml
# backend/src/config/model_config.yaml
models:
  intent_analyzer: "gemini-2.5-pro"
  planner: "gemini-pro"
  writer: "gemini-2.5-pro"
  evaluator: "claude-opus"
  search_primary: "o3-reasoner"
  search_secondary: "sonar-deep"
  qa_specialist: "o3-mini"
```

## 🚢 Deployment

### **Railway Deployment (Recommended)**

#### **1. Prepare for Deployment**

```bash
# Ensure no large files in Git
git status --porcelain | grep "^A.*\.next"  # Should return nothing

# Create production environment file
cp .env.railway.secure .env.railway
# Edit with your production values
```

#### **2. Deploy Backend**

```bash
# Login to Railway
railway login

# Create new project
railway new handywriterz-backend

# Add PostgreSQL and Redis
railway add postgresql
railway add redis

# Set environment variables
railway variables set OPENAI_API_KEY=your_key
railway variables set ANTHROPIC_API_KEY=your_key
railway variables set GEMINI_API_KEY=your_key
# ... set all required variables

# Deploy
railway up
```

#### **3. Deploy Frontend**

```bash
# Create frontend service
railway new handywriterz-frontend

# Set frontend environment variables
railway variables set NEXT_PUBLIC_BACKEND_URL=https://your-backend.railway.app
railway variables set NEXT_PUBLIC_APP_URL=https://your-frontend.railway.app

# Deploy
cd frontend && railway up
```

#### **4. Post-Deployment Setup**

```bash
# Run database migrations
railway run alembic upgrade head

# Verify health endpoints
curl https://your-backend.railway.app/health
curl https://your-frontend.railway.app/api/health
```

### **AWS Deployment**

#### **1. Infrastructure Setup**

```bash
# Using AWS CDK or CloudFormation
# Deploy RDS PostgreSQL with pgvector
# Deploy ElastiCache Redis
# Deploy ECS/Fargate services
# Configure ALB and Route53
```

#### **2. Container Deployment**

```dockerfile
# Production Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TORCH_CPU_ONLY=true

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

EXPOSE 8000

CMD ["gunicorn", "src.main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000"]
```

### **Docker Compose Deployment**

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile.railway
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/handywriterz
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: frontend
      dockerfile: Dockerfile
    environment:
      - NEXT_PUBLIC_BACKEND_URL=http://backend:8000
    ports:
      - "3000:3000"

  db:
    image: pgvector/pgvector:pg15
    environment:
      POSTGRES_DB: handywriterz
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## 📖 Usage

### **Basic Usage**

#### **1. Account Setup**

```bash
# Visit the frontend URL
https://your-app.railway.app

# Connect Web3 wallet (Dynamic.xyz)
# Or create account with email
```

#### **2. Upload Research Materials**

```javascript
// Supported file types
const supportedFiles = [
  'application/pdf',           // PDF documents
  'application/msword',        // Word documents
  'text/plain',               // Text files
  'audio/mpeg',               // Audio files (MP3)
  'video/mp4',                // Video files
  'image/jpeg',               // Images (JPG, PNG)
  'application/vnd.ms-excel'   // Excel files
];

// File limits
const limits = {
  maxFiles: 50,
  maxFileSize: 100 * 1024 * 1024,  // 100MB per file
  maxTotalSize: 500 * 1024 * 1024  // 500MB total
};
```

#### **3. Create Academic Content**

```markdown
**Example Prompt:**
"Write a 3000-word literature review on machine learning applications in healthcare, focusing on diagnostic imaging. Use Harvard citation style and include recent papers from 2023-2024. The review should be suitable for a Master's dissertation in Computer Science."

**File Context:**
- Upload relevant research papers (PDF)
- Include any existing notes (DOCX)
- Add interview transcripts (audio files)
- Provide data visualizations (images)
```

#### **4. Real-time Progress Tracking**

The platform provides live updates on the writing process:

```
✅ Intent Analysis Complete (2s)
⏳ Research Phase In Progress...
  ├─ ArXiv Search: 15 papers found
  ├─ Cross-reference Check: 8 citations verified  
  └─ Source Quality Assessment: In progress
🔄 Writing Phase: 1,247 / 3,000 words generated
⚠️  Quality Check: Bias detection running
✅ Plagiarism Score: 98% original content
📝 Citation Formatting: Harvard style applied
```

### **Advanced Usage**

#### **1. Multi-Modal Research Synthesis**

```python
# Example: Combining multiple data sources
research_materials = {
    "papers": ["research_paper_1.pdf", "review_2023.pdf"],
    "interviews": ["expert_interview.mp3", "focus_group.wav"],
    "data": ["survey_results.xlsx", "statistics.csv"],
    "visuals": ["graph_1.png", "diagram.jpg"]
}

# The system automatically:
# 1. Extracts text from PDFs
# 2. Transcribes audio using Whisper
# 3. Analyzes data patterns
# 4. Describes visual content
# 5. Synthesizes all information coherently
```

#### **2. Custom Academic Styles**

```yaml
# Custom citation style configuration
citation_style:
  name: "Imperial College London Style"  
  type: "numeric"
  format:
    in_text: "[{number}]"
    bibliography: "{authors}. {title}. {journal}. {year};{volume}({issue}):{pages}."
  sorting: "alphabetical"
  abbreviations:
    journal_names: true
    author_names: false
```

#### **3. Collaborative Workflows**

```javascript
// Team collaboration features
const collaboration = {
  shared_workspaces: true,
  real_time_editing: true,
  comment_system: true,
  version_control: true,
  role_permissions: {
    admin: ["read", "write", "manage", "export"],
    editor: ["read", "write", "comment"],
    reviewer: ["read", "comment"]
  }
};
```

### **API Usage Examples**

#### **1. File Upload API**

```python
import requests
from tus_client import TusClient

# Initialize TUS client for resumable uploads
client = TusClient("https://your-api.railway.app/api/files/upload")

# Upload file with metadata
file_path = "research_paper.pdf"
metadata = {
    "filename": "research_paper.pdf",
    "context": "literature_review",
    "academic_level": "masters",
    "subject": "computer_science"
}

upload_url = client.upload(file_path, metadata=metadata)
print(f"File uploaded: {upload_url}")
```

#### **2. Chat Completion API**

```python
import asyncio
import aiohttp

async def generate_content():
    payload = {
        "prompt": "Write a research methodology section for studying AI ethics",
        "mode": "academic_writing",
        "file_ids": ["file_123", "file_456"],
        "parameters": {
            "word_count": 1500,
            "citation_style": "harvard",
            "academic_level": "doctoral",
            "region": "uk"
        }
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://your-api.railway.app/api/chat",
            json=payload,
            headers={"Authorization": "Bearer your_jwt_token"}
        ) as response:
            async for line in response.content:
                if line.startswith(b"data: "):
                    data = json.loads(line[6:])
                    print(f"Progress: {data.get('progress', 0)}%")
                    if data.get("content"):
                        print(data["content"], end="", flush=True)

asyncio.run(generate_content())
```

#### **3. Quality Assessment API**

```python
# Check content quality and originality
assessment_response = requests.post(
    "https://your-api.railway.app/api/quality/assess",
    json={
        "content": "Your academic content here...",
        "check_plagiarism": True,
        "check_citations": True,
        "academic_level": "masters"
    },
    headers={"Authorization": "Bearer your_jwt_token"}
)

quality_report = assessment_response.json()
print(f"Originality Score: {quality_report['originality_score']}%")
print(f"Citation Accuracy: {quality_report['citation_accuracy']}%")
print(f"Academic Tone: {quality_report['academic_tone_score']}/10")
```

## 🔌 API Documentation

### **Core Endpoints**

#### **Authentication**
```http
POST /api/auth/login
POST /api/auth/register
POST /api/auth/refresh
DELETE /api/auth/logout
```

#### **File Management**
```http
POST /api/files/upload          # TUS resumable upload
GET /api/files/                 # List user files
GET /api/files/{file_id}        # Get file details
DELETE /api/files/{file_id}     # Delete file
POST /api/files/{file_id}/process  # Process uploaded file
```

#### **Chat & Content Generation**
```http
POST /api/chat                  # Generate academic content
GET /api/chat/history          # Get conversation history
GET /api/chat/{conversation_id} # Get specific conversation
DELETE /api/chat/{conversation_id} # Delete conversation
```

#### **Quality & Assessment**
```http
POST /api/quality/assess        # Quality assessment
POST /api/quality/plagiarism    # Plagiarism check
POST /api/quality/citations     # Citation validation
GET /api/quality/report/{id}    # Get quality report
```

#### **Administrative**
```http
GET /api/admin/models          # Get model configurations
PUT /api/admin/models/{model}  # Update model settings
GET /api/admin/usage          # Get usage statistics
GET /api/admin/users          # User management
```

### **WebSocket Events**

```javascript
// Connect to real-time updates
const ws = new WebSocket('wss://your-api.railway.app/ws/chat/{conversation_id}');

// Event types
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'progress':
            console.log(`Progress: ${data.percentage}%`);
            break;
        case 'content':
            console.log(`New content: ${data.text}`);
            break;
        case 'agent_update':
            console.log(`Agent ${data.agent} status: ${data.status}`);
            break;
        case 'cost_update':
            console.log(`Cost so far: $${data.cost_usd}`);
            break;
        case 'error':
            console.error(`Error: ${data.message}`);
            break;
        case 'complete':
            console.log('Generation complete!');
            break;
    }
};
```

### **Response Formats**

#### **Standard API Response**
```json
{
    "success": true,
    "data": {
        "id": "conv_123456",
        "content": "Generated academic content...",
        "metadata": {
            "word_count": 1247,
            "citations": 15,
            "originality_score": 98.5,
            "processing_time": 45.2
        }
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### **Error Response**
```json
{
    "success": false,
    "error": {
        "code": "INSUFFICIENT_CREDITS",
        "message": "Insufficient credits for this request",
        "details": {
            "required": 100,
            "available": 25,
            "cost_breakdown": {
                "input_tokens": 1200,
                "output_tokens": 3500,
                "model_cost": 0.02
            }
        }
    },
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🧪 Testing

### **Running Tests**

#### **Backend Tests**
```bash
# Unit tests
pytest backend/src/tests/ -v

# Integration tests  
pytest backend/src/tests/test_integration/ -v

# End-to-end tests
pytest backend/src/tests/test_e2e/ -v

# Test with coverage
pytest --cov=src --cov-report=html

# Performance tests
pytest backend/src/tests/test_performance/ -v --durations=10
```

#### **Frontend Tests**
```bash
# Unit tests
npm run test

# E2E tests with Playwright
npm run test:e2e

# Visual regression tests
npm run test:visual

# Performance tests
npm run test:lighthouse
```

### **Test Configuration**

#### **pytest.ini**
```ini
[tool:pytest]
testpaths = backend/src/tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

#### **Test Environment**
```bash
# Test environment variables
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_handywriterz
TEST_REDIS_URL=redis://localhost:6379/1
MOCK_AI_RESPONSES=true
DISABLE_RATE_LIMITING=true
```

### **Key Test Scenarios**

#### **1. Complete User Journey Test**
```python
async def test_complete_user_journey():
    """Test full academic writing workflow"""
    
    # 1. User registration
    user = await create_test_user()
    
    # 2. File upload
    file_id = await upload_test_file("research_paper.pdf")
    
    # 3. Content generation request
    conversation = await start_conversation({
        "prompt": "Write literature review",
        "file_ids": [file_id],
        "word_count": 1000
    })
    
    # 4. Wait for completion
    result = await wait_for_completion(conversation.id)
    
    # 5. Verify output quality
    assert result.word_count >= 900
    assert result.originality_score > 95
    assert len(result.citations) > 5
    
    # 6. Download and verify format
    download_url = await get_download_url(conversation.id, "docx")
    assert download_url is not None
```

#### **2. Multi-Agent System Test**
```python
async def test_multi_agent_coordination():
    """Test agent coordination and handoffs"""
    
    # Mock agent responses
    with mock_agents({
        "intent_analyzer": {"intent": "academic_writing"},
        "planner": {"outline": "5-section paper"},
        "research_swarm": {"sources": 10},
        "writing_swarm": {"content": "Generated content"},
        "qa_swarm": {"quality_score": 95}
    }):
        
        result = await process_academic_request(
            prompt="Write research paper",
            file_ids=[]
        )
        
        # Verify agent coordination
        assert result.agents_used == [
            "intent_analyzer", "planner", "research_swarm",
            "writing_swarm", "qa_swarm"
        ]
        assert result.processing_time < 60  # seconds
```

#### **3. Performance Benchmarks**
```python
@pytest.mark.performance
async def test_performance_benchmarks():
    """Test system performance under load"""
    
    # Concurrent requests
    tasks = []
    for i in range(10):
        task = generate_content(f"prompt_{i}")
        tasks.append(task)
    
    start_time = time.time()
    results = await asyncio.gather(*tasks)
    end_time = time.time()
    
    # Performance assertions
    assert end_time - start_time < 120  # 2 minutes for 10 requests
    assert all(r.success for r in results)
    assert all(r.processing_time < 30 for r in results)
```

## 🔧 Development

### **Development Setup**

#### **1. Development Environment**
```bash
# Install development dependencies
pip install -r backend/requirements-dev.txt
npm install --include=dev

# Set up pre-commit hooks
pre-commit install

# Start development servers
make dev  # Starts both backend and frontend
```

#### **2. Code Quality Tools**

```bash
# Python formatting and linting
black backend/src/
isort backend/src/
flake8 backend/src/
mypy backend/src/

# JavaScript/TypeScript formatting and linting  
npm run lint
npm run type-check
npm run format
```

#### **3. Database Development**

```bash
# Create new migration
alembic revision --autogenerate -m "Add new table"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Reset database (development only)
python backend/scripts/reset_db.py
```

### **Project Structure**

```
HandyWriterzAi/
├── backend/                    # FastAPI backend
│   ├── alembic/               # Database migrations
│   ├── src/
│   │   ├── agent/             # Multi-agent system
│   │   │   ├── nodes/         # Individual agent implementations
│   │   │   └── swarms/        # Agent coordination logic
│   │   ├── api/               # FastAPI routes
│   │   ├── core/              # Core application logic
│   │   ├── services/          # Business logic services
│   │   ├── models/            # Database models
│   │   └── tests/             # Test suites
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile.railway     # Production container
├── frontend/                  # Next.js frontend
│   ├── src/
│   │   ├── app/               # Next.js app router
│   │   ├── components/        # React components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utility functions
│   │   └── types/             # TypeScript definitions
│   ├── package.json           # Node.js dependencies
│   └── next.config.mjs        # Next.js configuration
├── docs/                      # Documentation
├── scripts/                   # Deployment and utility scripts
├── docker-compose.yml         # Development environment
├── docker-compose.prod.yml    # Production environment
├── railway.json               # Railway deployment config
└── README.md                  # This file
```

### **Contributing Guidelines**

#### **1. Development Workflow**

```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature description"

# 3. Run tests
make test

# 4. Push and create PR
git push origin feature/your-feature-name
```

#### **2. Commit Message Convention**

```
feat: add new feature
fix: resolve bug in user authentication
docs: update API documentation
style: format code with black
refactor: improve agent coordination logic
test: add unit tests for file processing
chore: update dependencies
```

#### **3. Code Review Checklist**

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] Performance impact is considered
- [ ] Security implications are reviewed
- [ ] Breaking changes are documented

### **Debugging**

#### **1. Backend Debugging**

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use debugger
import pdb; pdb.set_trace()

# Monitor agent execution
from src.core.monitoring import AgentMonitor
monitor = AgentMonitor()
monitor.track_agent_execution(agent_id="writer_001")
```

#### **2. Frontend Debugging**

```javascript
// Enable React DevTools
// Chrome extension: React Developer Tools

// Debug API calls
console.log('API Request:', payload);
console.log('API Response:', response);

// Monitor WebSocket events
ws.addEventListener('message', (event) => {
    console.log('WebSocket message:', JSON.parse(event.data));
});
```

#### **3. Database Debugging**

```bash
# Monitor database queries
tail -f /var/log/postgresql/postgresql-15-main.log

# Analyze slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

# Check database connections
SELECT count(*) FROM pg_stat_activity;
```

## 💼 Business Model

### **Pricing Tiers**

#### **Free Tier - Research Starter**
- **Price**: Free
- **Daily Budget**: $0.50 USD
- **Features**:
  - Basic academic writing assistance
  - 3 welcome credits ($1.50 value)
  - Standard AI models (Gemini Pro)
  - Up to 1,000 words per day
  - Basic citation support
  - Community support

#### **Pro Tier - Academic Professional**
- **Price**: $29/month or $290/year
- **Daily Budget**: $5.00 USD
- **Features**:
  - Advanced multi-agent system access
  - Premium AI models (GPT-4, Claude Opus)
  - Up to 10,000 words per day
  - Advanced citation management
  - Priority processing
  - Email support
  - Export to multiple formats

#### **Enterprise Tier - Institution**
- **Price**: $199/month or $1,990/year
- **Daily Budget**: $50.00 USD
- **Features**:
  - Full platform access
  - Custom model configurations
  - Unlimited word generation
  - Team collaboration features
  - API access and integrations
  - Dedicated account manager
  - Custom deployment options
  - SLA guarantee

### **Usage-Based Pricing**

```javascript
// Cost calculation example
const costCalculation = {
  inputTokens: 1500,
  outputTokens: 3000,
  modelUsed: "gemini-2.5-pro",
  
  baseCosts: {
    "gemini-pro": { input: 0.0005, output: 0.0015 },
    "gemini-2.5-pro": { input: 0.00125, output: 0.005 },
    "claude-opus": { input: 0.015, output: 0.075 },
    "gpt-4": { input: 0.03, output: 0.06 }
  },
  
  calculateCost: function() {
    const model = this.baseCosts[this.modelUsed];
    return (this.inputTokens * model.input + this.outputTokens * model.output) / 1000;
  }
};

// Example: $0.01688 for a typical request
```

### **Revenue Streams**

1. **Subscription Revenue**: Monthly/annual subscriptions
2. **Usage Overages**: Pay-per-use beyond daily limits
3. **Enterprise Licenses**: Custom pricing for institutions
4. **API Access**: Developer API usage fees
5. **White-label Solutions**: Custom deployments for partners

### **Market Analysis**

#### **Target Market Size**
- **Global Higher Education**: $750B market
- **AI Writing Tools**: $1.1B market (growing 25% YoY)
- **Academic Publishing**: $19B market
- **Total Addressable Market**: $50B+

#### **Competitive Advantages**
1. **Multi-Agent Architecture**: Unique approach vs single-model competitors
2. **Academic Focus**: Purpose-built for scholarly writing
3. **Citation Integrity**: Advanced plagiarism detection and proper referencing
4. **Multimodal Processing**: Handles diverse file types beyond text
5. **Production Ready**: Enterprise-grade infrastructure and security

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help make HandyWriterz better:

### **Ways to Contribute**

#### **1. Code Contributions**
- Fix bugs and implement new features
- Improve performance and optimization
- Add new AI model integrations
- Enhance user interface and experience

#### **2. Documentation**
- Improve README and setup guides
- Write tutorials and examples
- Create API documentation
- Translate documentation

#### **3. Testing**
- Write unit and integration tests
- Perform user acceptance testing
- Report bugs and issues
- Validate on different platforms

#### **4. Community**
- Answer questions in discussions
- Share usage examples
- Provide feedback and suggestions
- Help with user onboarding

### **Getting Started**

#### **1. Fork and Clone**
```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/your-username/HandyWriterzAi.git
cd HandyWriterzAi

# Add upstream remote
git remote add upstream https://github.com/Abelhubprog/HandyWriterzAi.git
```

#### **2. Set Up Development Environment**
```bash
# Follow the installation guide above
# Make sure all tests pass
make test
```

#### **3. Make Your Changes**
```bash
# Create a feature branch
git checkout -b feature/your-contribution

# Make changes and commit
git add .
git commit -m "feat: describe your changes"

# Push to your fork
git push origin feature/your-contribution
```

#### **4. Submit Pull Request**
- Create a pull request on GitHub
- Describe your changes clearly
- Link any related issues
- Wait for code review

### **Code of Conduct**

We are committed to providing a welcoming and inclusive environment for all contributors. Please read our [Code of Conduct](CODE_OF_CONDUCT.md) before participating.

### **Development Guidelines**

#### **Code Style**
- Python: Follow PEP 8, use Black formatter
- JavaScript/TypeScript: Follow Prettier and ESLint rules
- Write clear, self-documenting code
- Add type hints and JSDoc comments

#### **Testing Requirements**
- Write tests for new features
- Maintain >80% code coverage
- Ensure all tests pass before submitting
- Include both unit and integration tests

#### **Documentation Standards**
- Update README for new features
- Add docstrings to all functions
- Include usage examples
- Keep documentation current

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### **MIT License Summary**

- ✅ **Commercial Use**: Use the software for commercial purposes
- ✅ **Modification**: Modify the software and create derivative works
- ✅ **Distribution**: Distribute the software
- ✅ **Private Use**: Use the software for private purposes
- ❌ **Liability**: No warranty or liability provided
- ❌ **Warranty**: Software is provided "as is"

### **Attribution**

If you use HandyWriterz in your research or project, please cite:

```bibtex
@software{handywriterz2024,
  title={HandyWriterz: AI-Powered Academic Writing Platform},
  author={HandyWriterz Team},
  year={2024},
  url={https://github.com/Abelhubprog/HandyWriterzAi},
  version={1.0.0}
}
```

---

## 🚀 Get Started Today

Ready to revolutionize your academic writing? 

### **Quick Links**
- 🌐 **Live Demo**: [handywriterz.com](https://handywriterz.com)
- 📖 **Documentation**: [docs.handywriterz.com](https://docs.handywriterz.com)
- 💬 **Community**: [Discord](https://discord.gg/handywriterz)
- 🐛 **Issues**: [GitHub Issues](https://github.com/Abelhubprog/HandyWriterzAi/issues)

### **Support**
- 📧 **Email**: support@handywriterz.com
- 💬 **Chat**: Live chat on website
- 📖 **Knowledge Base**: [help.handywriterz.com](https://help.handywriterz.com)

---

<div align="center">

**Built with ❤️ by the HandyWriterz Team**

*Transforming academic writing with AI, one paper at a time.*

[![GitHub stars](https://img.shields.io/github/stars/Abelhubprog/HandyWriterzAi?style=social)](https://github.com/Abelhubprog/HandyWriterzAi/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Abelhubprog/HandyWriterzAi?style=social)](https://github.com/Abelhubprog/HandyWriterzAi/network)
[![Twitter Follow](https://img.shields.io/twitter/follow/HandyWriterzAI?style=social)](https://twitter.com/HandyWriterzAI)

</div>