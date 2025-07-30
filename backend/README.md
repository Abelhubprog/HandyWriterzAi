# 🚀 Unified AI Platform - Revolutionary Multi-Agent System

## Overview

The **Unified AI Platform** is an intelligent multi-agent system that seamlessly combines:

- **Simple Gemini System**: Fast responses for quick queries and basic tasks
- **Advanced HandyWriterz System**: Comprehensive academic writing with 30+ specialized agents
- **Intelligent Routing**: Automatic system selection based on request complexity analysis

## ✨ Key Features

### 🎯 Intelligent Routing
- **Automatic System Selection**: Analyzes request complexity (1-10 scale) and routes optimally
- **Academic Detection**: Essays, research papers automatically use advanced system
- **Hybrid Processing**: Parallel execution for medium-complexity tasks
- **Graceful Fallbacks**: Robust error handling with system switching

### 🧠 Advanced Multi-Agent System
- **30+ Specialized Agents**: Research swarms, QA swarms, writing swarms
- **Master Orchestrator**: 9-phase workflow optimization
- **Swarm Intelligence**: Emergent behavior from agent collaboration
- **Quality Assurance**: Multi-tier evaluation and validation

### ⚡ Performance Optimization
- **Smart Caching**: Redis-based caching for faster responses
- **Parallel Processing**: Hybrid mode runs both systems simultaneously
- **Circuit Breakers**: Automatic failover and recovery
- **Load Balancing**: Optimal resource utilization

## 🏗️ Architecture

```
Unified AI Platform
├── Intelligent Router
│   ├── Complexity Analyzer (1-10 scale)
│   ├── Academic Detection
│   └── System Selection Logic
├── Simple Gemini System
│   ├── Quick Chat Responses
│   ├── Basic Research
│   └── Fast Processing (<3s)
└── Advanced HandyWriterz System
    ├── Master Orchestrator
    ├── Research Swarms (5+ agents)
    ├── QA Swarms (5+ agents)
    ├── Writing Swarms (5+ agents)
    ├── Citation Management
    ├── Quality Assessment
    └── Academic Formatting
```

## 📊 Routing Logic

| Query Type | Complexity Score | System Used | Response Time |
|------------|------------------|-------------|---------------|
| "What is AI?" | 2.0 | Simple | 1-3 seconds |
| "Explain machine learning" | 5.5 | Hybrid | 30-60 seconds |
| "Write a 5-page essay on climate change" | 8.5 | Advanced | 2-5 minutes |
| File uploads + analysis | 6.0+ | Advanced/Hybrid | 1-10 minutes |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Redis (for caching and SSE)
- PostgreSQL with pgvector (for advanced features)

### 1. Automated Setup
```bash
cd backend/backend
python setup.py
```

### 2. Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Start services
redis-server  # In another terminal
# PostgreSQL setup (optional for advanced features)

# Run the server
python src/main.py
```

### 3. Verify Installation
```bash
# Check system status
curl http://localhost:8000/api/status

# Test routing analysis
curl -X POST "http://localhost:8000/api/analyze" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Write a research paper on artificial intelligence"
```

## 🎮 Usage Examples

### Simple Chat Query
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=What is artificial intelligence?"

# Response: Fast answer from Gemini system
```

### Academic Writing Request
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=Write a 3-page academic essay on climate change impacts" \
  -d "user_params={\"writeupType\":\"essay\",\"pages\":3,\"field\":\"environmental science\"}"

# Response: Full HandyWriterz workflow with research, writing, and citations
```

### File Analysis
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -F "message=Analyze this document and provide insights" \
  -F "files=@document.pdf"

# Response: Advanced system processes file with context analysis
```

## 📡 API Endpoints

### Core Endpoints
- `POST /api/chat` - Unified chat with intelligent routing
- `POST /api/chat/simple` - Force simple system (fast responses)
- `POST /api/chat/advanced` - Force advanced system (academic writing)
- `GET /api/status` - System status and capabilities
- `POST /api/analyze` - Analyze request complexity (development)

### Advanced Features
- `POST /api/write` - Academic writing workflow
- `POST /api/upload` - File upload and processing
- `GET /api/stream/{conversation_id}` - Real-time SSE updates
- `GET /api/conversation/{conversation_id}` - Conversation status

### Documentation
- `GET /docs` - Interactive API documentation
- `GET /health` - Health check endpoint

## ⚙️ Configuration

### Environment Variables

```bash
# System Configuration
SYSTEM_MODE=hybrid                    # simple, advanced, or hybrid
SIMPLE_SYSTEM_ENABLED=true
ADVANCED_SYSTEM_ENABLED=true

# Routing Thresholds
SIMPLE_MAX_COMPLEXITY=4.0           # Queries ≤ 4.0 use simple system
ADVANCED_MIN_COMPLEXITY=7.0         # Queries ≥ 7.0 use advanced system

# AI Provider Keys
GEMINI_API_KEY=your_gemini_key      # Required for simple system
ANTHROPIC_API_KEY=your_claude_key   # Required for advanced system
OPENAI_API_KEY=your_openai_key      # Optional enhancement
PERPLEXITY_API_KEY=your_perplexity_key  # Optional research

# Database & Cache
DATABASE_URL=postgresql://handywriterz:password@localhost/handywriterz
REDIS_URL=redis://localhost:6379

# Security
JWT_SECRET_KEY=your_secure_secret_key
ENVIRONMENT=development
```

### Routing Customization

Adjust complexity thresholds in `.env`:
```bash
SIMPLE_MAX_COMPLEXITY=3.0    # More queries use advanced system
ADVANCED_MIN_COMPLEXITY=8.0  # Fewer queries use advanced system
```

## 🧪 Testing

### Unit Tests
```bash
python -m pytest tests/ -v
```

### Integration Tests
```bash
python scripts/test_routing.py
```

### Performance Benchmarks
```bash
python scripts/benchmark.py
```

### Manual Testing
```bash
# Test different query types
python examples/simple_query.py
python examples/advanced_query.py  
python examples/hybrid_query.py
```

## 📊 Monitoring

### System Metrics
```bash
# Get comprehensive system status
curl http://localhost:8000/api/status

# Response includes:
# - System availability (simple/advanced)
# - Routing statistics and thresholds
# - Infrastructure health (Redis, DB)
# - Performance metrics
```

### Routing Analysis
```bash
# Analyze how requests would be routed
curl -X POST "http://localhost:8000/api/analyze" \
  -d "message=Your query here"

# Response includes:
# - Complexity score calculation
# - Routing decision and confidence
# - Estimated processing time
# - System recommendation
```

## 🔧 Development

### Project Structure
```
backend/backend/
├── src/
│   ├── agent/
│   │   ├── simple/                   # Simple system integration
│   │   ├── routing/                  # Intelligent routing logic
│   │   ├── handywriterz_graph.py     # Advanced system
│   │   └── nodes/                    # 30+ specialized agents
│   ├── api/                          # (Future: Organized endpoints)
│   ├── db/                           # Database layer
│   ├── services/                     # Business services
│   ├── middleware/                   # Security & error handling
│   └── main.py                       # Application entry point
├── docs/                             # (Future: Documentation)
├── examples/                         # (Future: Usage examples)
├── scripts/                          # (Future: Utility scripts)
├── .env.example                      # Configuration template
├── requirements.txt                  # Dependencies
├── setup.py                          # Automated setup
└── README.md                         # This file
```

### Adding New Features
1. **New AI Provider**: Add to routing logic in `agent/routing/`
2. **New Endpoints**: Add to `main.py` or create in `api/` module
3. **New Agents**: Add to `agent/nodes/` with swarm integration
4. **Routing Logic**: Modify `ComplexityAnalyzer` in `agent/routing/`

## 🚨 Troubleshooting

### Common Issues

#### 1. Simple System Not Available
```bash
# Check if Gemini API key is set
echo $GEMINI_API_KEY

# Verify simple system imports
python -c "from src.agent.simple import SIMPLE_SYSTEM_READY; print(SIMPLE_SYSTEM_READY)"
```

#### 2. Advanced System Errors
```bash
# Check database connection
python -c "from src.db.database import db_manager; print(db_manager.health_check())"

# Verify all dependencies
pip install -r requirements.txt
```

#### 3. Routing Issues
```bash
# Test routing logic
curl -X POST "http://localhost:8000/api/analyze" -d "message=test query"

# Check routing thresholds in logs
tail -f handywriterz.log | grep "Routing decision"
```

#### 4. Performance Issues
```bash
# Check system resources
curl http://localhost:8000/api/status

# Monitor Redis
redis-cli info

# Check database performance
psql -d handywriterz -c "SELECT COUNT(*) FROM conversations;"
```

## 🤝 Contributing

### Development Setup
```bash
# Clone and setup
git clone <repository>
cd backend/backend
python setup.py

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/ -v

# Check code quality
black src/
isort src/
flake8 src/
```

### Pull Request Process
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Update documentation
6. Submit pull request

## 📞 Support

### Documentation
- **API Docs**: http://localhost:8000/docs
- **System Status**: http://localhost:8000/api/status
- **Architecture**: See `structure.md`

### Community
- **Issues**: Create GitHub issue for bugs/features
- **Discussions**: Join community discussions
- **Email**: contact@unifiedai.platform

## 🔮 Roadmap

### Short Term (1-2 months)
- [ ] Additional AI provider integrations (Claude, DeepSeek, Qwen)
- [ ] Enhanced frontend with routing visualization
- [ ] Real-time collaboration features
- [ ] Mobile application

### Medium Term (3-6 months)
- [ ] Multi-platform deployment (Docker, Kubernetes)
- [ ] Advanced analytics and monitoring
- [ ] Enterprise security features
- [ ] Educational institution partnerships

### Long Term (6+ months)
- [ ] Open-source routing framework
- [ ] Industry partnerships
- [ ] Research publications
- [ ] Global educational impact

## 📄 License

[License information - update as needed]

## 🙏 Acknowledgments

Built on the foundation of:
- **HandyWriterz**: Advanced multi-agent academic writing system
- **Google Gemini**: Fast and efficient AI responses
- **LangGraph**: Agent orchestration framework
- **FastAPI**: High-performance web framework

---

**Ready to experience the future of intelligent AI routing?** 🚀

Start with: `python setup.py` and visit `http://localhost:8000/docs`