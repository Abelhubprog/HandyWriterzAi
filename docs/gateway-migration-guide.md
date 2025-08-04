# LLM Gateway Migration Guide

## Overview
This guide provides step-by-step instructions for migrating your HandyWriterz AI system to use the new pluggable LLM Gateway with OpenRouter integration and intelligent model selection.

## Pre-Migration Checklist

### Requirements
- [ ] OpenRouter API key configured
- [ ] Redis available for caching and overrides
- [ ] Backup of current model configurations
- [ ] Test environment prepared

### Environment Variables
Add these to your environment:
```bash
# OpenRouter Integration
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Gateway Configuration
ENABLE_GATEWAY_V2=true
ENABLE_MODEL_TRACING=true
ENABLE_COST_OPTIMIZATION=true

# Fallback Settings
GATEWAY_FALLBACK_ENABLED=true
GATEWAY_MAX_RETRIES=3
GATEWAY_RETRY_DELAY=1.0

# Performance Monitoring
GATEWAY_METRICS_RETENTION_HOURS=168
GATEWAY_TRACE_SAMPLING_RATE=1.0
```

## Migration Phases

### Phase 1: Foundation Setup (Zero Risk)

#### 1.1 Install Gateway System
```bash
# No changes to existing code - just add new modules
cp -r src/services/gateway.py backend/src/services/
cp -r src/services/model_policy.py backend/src/services/
cp -r src/services/model_selector.py backend/src/services/
cp -r src/services/tracing.py backend/src/services/
cp -r src/services/node_integration.py backend/src/services/
```

#### 1.2 Create Configuration Files
```bash
mkdir -p backend/config

# Create model policies configuration
cat > backend/config/model_policies.yaml << 'EOF'
policies:
  # OpenRouter models
  gemini-2.5-pro:
    provider: openrouter
    provider_model_id: google/gemini-2.0-flash-exp
    capabilities:
      streaming: true
      function_calling: true
      long_context: true
      creative_writing: true
    cost_tier: MEDIUM
    context_window: 32000
    input_cost_per_1k: 0.00015
    output_cost_per_1k: 0.0006
    fallback_models: [claude-sonnet, gpt-4o]
    
  claude-sonnet:
    provider: openrouter
    provider_model_id: anthropic/claude-3.5-sonnet-20241022
    capabilities:
      streaming: true
      reasoning: true
      function_calling: true
    cost_tier: HIGH
    context_window: 200000
    input_cost_per_1k: 0.003
    output_cost_per_1k: 0.015
    fallback_models: [gpt-4o, gemini-2.5-pro]
EOF

# Create node requirements
cat > backend/config/node_requirements.yaml << 'EOF'
nodes:
  writer:
    required_capabilities: [streaming, creative_writing]
    preferred_capabilities: [long_context, function_calling]
    min_context_window: 8000
    max_cost_tier: HIGH
    
  evaluator:
    required_capabilities: [reasoning]
    preferred_capabilities: [function_calling]
    min_context_window: 8000
    max_cost_tier: PREMIUM
    reasoning_required: true
    
  search_perplexity:
    required_capabilities: [web_search]
    preferred_capabilities: [streaming]
    min_context_window: 16000
    max_cost_tier: HIGH
EOF
```

#### 1.3 Test Gateway Initialization
```python
# Test script: test_gateway_init.py
import asyncio
from src.services.gateway import get_llm_gateway
from src.services.model_policy import get_model_policy_registry
from src.services.model_selector import get_model_selector

async def test_gateway():
    # Test policy registry
    registry = get_model_policy_registry()
    policies = registry.get_all_policies()
    print(f"Loaded {len(policies)} policies")
    
    # Test model selector
    selector = get_model_selector()
    result = await selector.select_model(
        SelectionContext(node_name="test", capabilities=["streaming"])
    )
    print(f"Selected model: {result.selected_model.logical_id}")
    
    # Test gateway health
    gateway = get_llm_gateway()
    health = await gateway.health_check()
    print(f"Gateway health: {health['overall_status']}")

# Run test
asyncio.run(test_gateway())
```

### Phase 2: Gradual Agent Migration (Low Risk)

#### 2.1 Migrate One Agent Node
Start with a non-critical agent like `formatter`:

```python
# Before (formatter.py)
from src.services.llm_service import get_llm_client
model_client = get_llm_client("formatting", "gemini-2.5-flash")

# After (formatter.py) 
from src.services.node_integration import get_node_client_factory
client_factory = get_node_client_factory()
model_client = client_factory.create_formatter_client("formatter")
```

#### 2.2 Test Migration
```bash
# Run formatter tests
python -m pytest tests/test_formatter.py -v

# Check performance
curl -X POST localhost:8000/api/admin/gateway/test-selection \
  -H "Content-Type: application/json" \
  -d '{"node_name": "formatter", "capabilities": ["streaming"]}'
```

#### 2.3 Monitor Performance
```python
# Check metrics after 24 hours
import asyncio
from src.services.model_selector import get_model_selector

async def check_performance():
    selector = get_model_selector()
    metrics = await selector.get_model_recommendations("formatter")
    print(f"Performance data: {metrics['performance_data']}")

asyncio.run(check_performance())
```

### Phase 3: Core Agent Migration (Medium Risk)

#### 3.1 Migrate Writer Agent
```python
# Update writer.py to use new system
# See: backend/src/agent/nodes/writer_migrated.py for full example

class WriterAgent(StreamingNode):
    def __init__(self):
        super().__init__("writer")
        # NEW: Use capability-aware client factory
        self.client_factory = get_node_client_factory()
    
    async def execute(self, state, config):
        # NEW: Request capabilities instead of hardcoding model
        writer_client = self.client_factory.create_writer_client(
            node_name="writer",
            strategy=SelectionStrategy.BALANCED,
            trace_id=state.get("trace_id")
        )
        
        # Rest of logic unchanged
        response = await writer_client.ainvoke(messages)
        return {"content": response.content}
```

#### 3.2 Validate Quality
```bash
# Run full writing pipeline tests
python -m pytest tests/test_writer.py::test_full_pipeline -v

# Compare outputs
python scripts/compare_writer_outputs.py --old-model gemini-2.5-pro --new-gateway
```

### Phase 4: Full System Migration (Higher Risk)

#### 4.1 Migrate All Remaining Agents
Apply the same pattern to:
- `search_*` agents
- `evaluator` agents  
- `qa_*` agents
- `citation_master`

#### 4.2 Update API Endpoints
```python
# Add new endpoints to main.py
from src.routes.admin_gateway import admin_gateway_router
from src.routes.chat_gateway import chat_gateway_router

app.include_router(admin_gateway_router)
app.include_router(chat_gateway_router)
```

#### 4.3 Add Middleware
```python
# Update main.py
from src.middleware.gateway_middleware import GatewayMiddleware

app.add_middleware(GatewayMiddleware)
```

### Phase 5: Production Deployment

#### 5.1 Feature Flags
```python
# settings.py
class Settings(BaseSettings):
    # Gradual rollout flags
    GATEWAY_V2_ENABLED: bool = False
    GATEWAY_V2_PERCENTAGE: int = 0  # 0-100% of requests
    OPENROUTER_FALLBACK_ENABLED: bool = True
```

#### 5.2 Monitoring Setup
```python
# monitoring.py
import logging
from src.services.tracing import get_tracer

# Set up structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(name)s %(levelname)s %(message)s'
)

# Monitor key metrics
async def monitor_gateway():
    tracer = get_tracer()
    metrics = await tracer.get_trace_metrics(hours=1)
    
    if metrics.get("error_rate", 0) > 0.05:  # 5% error rate
        logging.error(f"High error rate: {metrics['error_rate']}")
    
    if metrics.get("avg_duration_ms", 0) > 5000:  # 5s latency
        logging.warning(f"High latency: {metrics['avg_duration_ms']}ms")
```

## Rollback Plan

### Immediate Rollback (Emergency)
```bash
# 1. Disable feature flags
export GATEWAY_V2_ENABLED=false
export OPENROUTER_FALLBACK_ENABLED=false

# 2. Restart services
systemctl restart handywriterz-backend

# 3. Switch DNS/load balancer to old version if needed
```

### Gradual Rollback (Planned)
```python
# Gradually reduce traffic to new system
GATEWAY_V2_PERCENTAGE = 50  # Reduce from 100% to 50%
# Monitor for 1 hour
GATEWAY_V2_PERCENTAGE = 25  # Further reduce
# Monitor for 1 hour  
GATEWAY_V2_PERCENTAGE = 0   # Complete rollback
```

## Validation Checklist

### Functional Testing
- [ ] All agent nodes can execute successfully
- [ ] Model selection works for different capability combinations
- [ ] Fallback models activate when primary fails
- [ ] Admin overrides take effect immediately
- [ ] Cost tracking accurately reflects usage
- [ ] Tracing captures all LLM requests

### Performance Testing
- [ ] Response times within 10% of baseline
- [ ] Memory usage stable under load
- [ ] No memory leaks after 24h operation
- [ ] Redis usage remains bounded
- [ ] OpenRouter rate limits respected

### Integration Testing
- [ ] Frontend streaming still works
- [ ] Legacy endpoints maintain compatibility
- [ ] Admin API functions correctly
- [ ] Budget limits are enforced
- [ ] Error handling graceful

### Business Logic Testing
- [ ] Output quality maintained or improved
- [ ] Cost optimization shows measurable savings
- [ ] Academic compliance still passes
- [ ] Citation accuracy unchanged

## Monitoring and Alerting

### Key Metrics to Track
```python
# metrics.py
GATEWAY_METRICS = {
    'request_count': 'Total LLM requests',
    'error_rate': 'Percentage of failed requests',
    'avg_latency': 'Average response time',
    'cost_per_request': 'Average cost per request',
    'model_distribution': 'Usage by model',
    'capability_usage': 'Most requested capabilities'
}
```

### Alerts Configuration
```yaml
# alerts.yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 5%
    action: page_oncall
    
  - name: high_latency
    condition: avg_latency > 10s
    action: slack_alert
    
  - name: cost_spike
    condition: hourly_cost > $50
    action: email_admin
    
  - name: model_failures
    condition: model_consecutive_failures > 5
    action: auto_disable_model
```

## Admin Operations Guide

### Daily Operations
```bash
# Check gateway health
curl -X GET localhost:8000/api/admin/gateway/health

# Review cost optimization opportunities
curl -X GET localhost:8000/api/admin/gateway/cost-optimization

# Check recent traces for errors  
curl -X GET localhost:8000/api/admin/gateway/traces?hours=1
```

### Model Management
```bash
# Update model for specific node
curl -X PUT localhost:8000/api/admin/gateway/policies/writer \
  -H "Content-Type: application/json" \
  -d '{"model_id": "claude-sonnet", "mode": "override"}'

# Bulk update models
curl -X PUT localhost:8000/api/admin/gateway/policies/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "updates": {
      "writer": "gemini-2.5-pro",
      "evaluator": "claude-sonnet"
    }
  }'

# Reload configuration from files
curl -X POST localhost:8000/api/admin/gateway/policies/reload
```

### Troubleshooting
```bash
# Validate configuration
curl -X GET localhost:8000/api/admin/gateway/validate

# Get detailed trace
curl -X GET localhost:8000/api/admin/gateway/traces/{trace_id}

# Check model recommendations
curl -X GET localhost:8000/api/admin/gateway/recommendations/writer
```

## Success Criteria

### Technical Success
- [ ] 99.9% uptime during migration
- [ ] <2% increase in average latency
- [ ] Zero data loss or corruption
- [ ] All existing functionality preserved

### Business Success  
- [ ] 15-30% reduction in AI model costs
- [ ] Improved response quality scores
- [ ] Enhanced admin control capabilities
- [ ] Future-ready for new AI models

### Operational Success
- [ ] Team trained on new admin interface
- [ ] Monitoring and alerting operational
- [ ] Documentation complete and accessible
- [ ] Rollback procedures tested and validated

## Post-Migration Tasks

1. **Performance Optimization**: Fine-tune model selection based on 30 days of data
2. **Cost Analysis**: Generate cost savings report
3. **Team Training**: Train support team on new admin tools
4. **Documentation**: Update operational runbooks
5. **Cleanup**: Remove old model configuration code after 90 days

This migration plan ensures a safe, gradual transition to the new LLM Gateway system while maintaining full operational capability throughout the process.