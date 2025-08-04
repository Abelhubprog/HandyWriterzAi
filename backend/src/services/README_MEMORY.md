# Memory Integration System - HandyWriterzAI

## Overview

The Memory Integration System provides production-ready long-term memory capabilities for HandyWriterzAI, enabling intelligent storage, retrieval, and adaptive management of user memories with importance ranking, vector similarity search, and AI-powered reflection.

## Key Features

### 🧠 Intelligent Memory Management
- **Vector-based Semantic Search**: Uses OpenAI embeddings with pgvector for similarity matching
- **Importance Scoring**: Adaptive importance calculation with temporal decay
- **Memory Types**: Episodic, Semantic, Procedural, Preference, and Contextual memories
- **Duplicate Detection**: Prevents redundant memory storage
- **Access Pattern Learning**: Boosts frequently accessed memories

### 🛡️ Production Safety Controls
- **PII Detection & Sanitization**: Automatic detection and masking of sensitive information
- **Rate Limiting**: Per-user limits on memory operations
- **Cost Tracking**: Real-time monitoring of embedding and LLM costs
- **Content Validation**: Spam detection and content length limits
- **Memory Limits**: Configurable per-user memory quotas

### 🔄 Adaptive Learning
- **AI Reflection**: Automatic extraction of insights from conversations
- **Importance Decay**: Time-based importance reduction with access-based boosting
- **Memory Maintenance**: Automated cleanup of old, low-importance memories
- **Vector Index Optimization**: Performance tuning for large-scale deployments

## Architecture

### Core Components

1. **MemoryIntegratorService** (`memory_integrator.py`)
   - Main service class handling all memory operations
   - Retrieval with hybrid scoring (similarity + importance + recency)
   - Memory writing with deduplication and safety checks
   - AI-powered reflection for automated memory extraction

2. **MemorySafetyService** (`memory_safety.py`)
   - PII detection and content sanitization
   - Rate limiting and cost tracking
   - Safety validation for all operations
   - User limit enforcement

3. **Enhanced Memory Nodes** (`agent/nodes/`)
   - `MemoryIntegratorNode`: Retrieves and injects memory context
   - `MemoryWriterNode`: Extracts and stores workflow insights
   - `MemoryMaintenanceNode`: Performs cleanup operations

4. **API Endpoints** (`api/memory.py`)
   - RESTful API for memory operations
   - Health checks and statistics
   - Admin maintenance endpoints

### Database Schema

The system extends your existing database with three new tables:

- **`long_term_memory`**: Core memory storage with vector embeddings
- **`memory_retrievals`**: Tracks retrieval patterns for adaptive scoring
- **`memory_reflections`**: Stores AI reflection sessions

## Usage

### Basic Memory Operations

```python
from services.memory_integrator import get_memory_integrator

memory_service = get_memory_integrator()

# Store a memory
memory_id = await memory_service.write_memory(
    user_id="user_123",
    content="User prefers APA citation style for psychology papers",
    memory_type=MemoryType.PREFERENCE,
    importance_score=0.8,
    tags=["citation", "psychology", "preference"]
)

# Retrieve relevant memories
memories = await memory_service.retrieve_memories(
    user_id="user_123",
    query="citation style preferences",
    k=5
)

# Perform AI reflection
reflection_memories = await memory_service.reflect_and_extract_memories(
    user_id="user_123",
    conversation_id="conv_456",
    conversation_context="...",
    user_response="..."
)
```

### Integration with Existing Workflow

The memory system integrates seamlessly with your existing LangGraph workflow:

```python
# In your graph definition
from agent.nodes.memory_integrator_node import MemoryIntegratorNode, MemoryWriterNode

# Add memory nodes to your graph
memory_retriever = MemoryIntegratorNode("memory_context")
memory_writer = MemoryWriterNode("memory_storage")

# Connect in your workflow
graph.add_edge("start", "memory_context")
graph.add_edge("memory_context", "writer")
graph.add_edge("writer", "memory_storage")
```

### API Usage

```bash
# Create a memory
curl -X POST "/api/memory/create?user_id=user_123" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "User prefers Harvard citation style",
    "memory_type": "preference",
    "importance_score": 0.8,
    "tags": ["citation", "harvard"]
  }'

# Retrieve memories
curl -X POST "/api/memory/retrieve?user_id=user_123" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "citation preferences",
    "k": 5
  }'

# Get memory statistics
curl "/api/memory/stats?user_id=user_123"
```

## Configuration

The system is configured via `config/memory_config.yaml`:

```yaml
memory_integrator:
  max_memories_per_user: 10000
  default_importance_threshold: 0.3
  retrieval_limit: 8

safety:
  rate_limits:
    max_memories_per_hour: 100
    max_retrievals_per_minute: 50
  cost_limits:
    max_daily_cost_per_user: 5.0
```

## Deployment

### Database Migration

Run the database migration to create the new memory tables:

```python
from db.database import get_db_manager
from db.models import Base

db_manager = get_db_manager()
Base.metadata.create_all(bind=db_manager.engine)
```

### Environment Variables

Ensure these environment variables are set:

```env
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
```

### Memory Maintenance

Set up automated maintenance using the provided script:

```bash
# Daily maintenance cron job
0 2 * * * /path/to/python /path/to/backend/src/scripts/memory_maintenance.py

# User-specific maintenance
python scripts/memory_maintenance.py --user-id user_123

# Dry run to see what would be done
python scripts/memory_maintenance.py --dry-run --verbose
```

## Memory Types

### 1. Episodic Memories
- **Purpose**: Store specific experiences and events
- **Examples**: "User completed a dissertation on machine learning", "User had difficulty with APA formatting"
- **Decay**: Standard rate (weekly 5% decay)

### 2. Semantic Memories  
- **Purpose**: Facts, concepts, and general knowledge
- **Examples**: "User studies computer science", "User's field is artificial intelligence"
- **Decay**: Slower rate (retains knowledge longer)

### 3. Procedural Memories
- **Purpose**: Skills and learned processes
- **Examples**: "User follows a specific outline structure", "User prefers step-by-step explanations"
- **Decay**: Very slow (skills persist)

### 4. Preference Memories
- **Purpose**: User preferences and patterns
- **Examples**: "User prefers Harvard citations", "User likes detailed explanations"
- **Decay**: Slowest rate (preferences are stable)

### 5. Contextual Memories
- **Purpose**: Context-dependent information
- **Examples**: "In academic writing, user prefers formal tone", "For business reports, user uses bullet points"
- **Decay**: Faster rate (context changes frequently)

## Performance Optimization

### Vector Index Tuning

The system uses HNSW indexes for optimal vector search performance:

```sql
-- Automatically created by the system
CREATE INDEX ix_memory_embedding_hnsw 
ON long_term_memory 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
```

### Caching Strategy

- **Memory Context Caching**: Frequently accessed memories cached in Redis
- **Embedding Caching**: Duplicate content detection with hash-based caching
- **Query Result Caching**: Similar queries cached for 5 minutes

### Monitoring

Track key metrics:

- Memory retrieval latency
- Embedding generation time
- Cost per user per day
- Memory effectiveness scores
- Storage usage trends

## Safety and Compliance

### PII Protection

The system automatically detects and masks:
- Email addresses → `[EMAIL]`
- Phone numbers → `[PHONE]` 
- Credit cards → `[CREDIT_CARD]`
- API keys → `[API_KEY]`
- URLs with parameters → `[URL]`
- IP addresses → `[IP_ADDRESS]`

### Cost Controls

- Daily spending limits per user
- Rate limiting on expensive operations
- Automatic cost tracking and alerting
- Memory cleanup to prevent runaway storage costs

### Rate Limiting

- 100 memories per hour per user
- 50 retrievals per minute per user
- 10 AI reflection calls per hour per user

## Troubleshooting

### Common Issues

1. **High Memory Costs**
   - Check user daily limits: `GET /api/memory/stats?user_id=X`
   - Review memory maintenance logs
   - Adjust importance thresholds to reduce storage

2. **Slow Retrieval Performance**
   - Verify vector indexes are created
   - Check PostgreSQL query performance
   - Consider increasing connection pool size

3. **PII Detection False Positives**
   - Review PII patterns in `memory_safety.py`
   - Allow PII for specific users if needed
   - Customize sanitization rules

4. **Memory Quality Issues**
   - Adjust reflection prompts
   - Review importance scoring algorithm
   - Check duplicate detection thresholds

### Logs and Monitoring

Monitor these log patterns:

```
INFO - Memory retrieval completed: 8 memories for user_123
WARN - Rate limit exceeded for user_456, operation retrieval  
ERROR - Memory writing failed for user_789: validation error
INFO - Memory maintenance: updated 1250, cleaned 45 memories
```

## Contributing

When extending the memory system:

1. **Safety First**: Always add safety checks for new operations
2. **Cost Tracking**: Track costs for any new LLM or embedding calls
3. **Testing**: Add comprehensive tests for new functionality
4. **Documentation**: Update this README and code comments

## Future Enhancements

- **Collaborative Memories**: Share insights across similar users
- **Memory Compression**: Summarize old memories to save storage
- **Advanced Analytics**: Memory effectiveness scoring and optimization
- **Multi-modal Memories**: Support for image and audio memories
- **Federated Learning**: Learn from usage patterns while preserving privacy

---

*This memory integration system provides a solid foundation for production deployment while maintaining safety, performance, and cost-effectiveness.*