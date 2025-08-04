# Next.js Frontend Integration Guide

## Overview
This guide covers integrating your Next.js frontend with the new LLM Gateway system for enhanced AI model selection, streaming, and cost optimization.

## Key Benefits
- **Intelligent Model Selection**: Frontend can hint at required capabilities
- **Real-time Streaming**: Enhanced SSE with model metadata
- **Cost Transparency**: Display estimated and actual costs to users
- **Performance Insights**: Show which models are being used and why

## API Changes

### Enhanced Chat Completion

**Old API:**
```typescript
const response = await fetch('/api/chat/send', {
  method: 'POST',
  body: JSON.stringify({
    messages: [{role: 'user', content: 'Hello'}],
    mode: 'general'
  })
});
```

**New API:**
```typescript
const response = await fetch('/api/chat/complete', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    messages: [{role: 'user', content: 'Hello'}],
    node_name: 'chat_completion',
    capabilities: ['streaming', 'creative_writing'],
    strategy: 'balanced',
    temperature: 0.7
  })
});

const data = await response.json();
// New response includes:
// - model_used: "gemini-2.5-pro"
// - provider: "openrouter" 
// - cost_usd: 0.0023
// - latency_ms: 1250
// - trace_id: "abc-123"
```

### Enhanced Streaming

**Frontend Implementation:**
```typescript
const streamChat = async (messages: Message[], capabilities: string[] = []) => {
  const response = await fetch('/api/chat/stream', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      messages,
      capabilities,
      strategy: 'balanced'
    })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n');
    
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const data = JSON.parse(line.slice(6));
        
        switch (data.type) {
          case 'metadata':
            // Show selected model and reasoning
            setModelInfo({
              model: data.model,
              provider: data.provider,
              reasoning: data.reasoning,
              estimatedCost: data.estimated_cost
            });
            break;
            
          case 'content':
            // Stream content as before
            setContent(prev => prev + data.token);
            break;
            
          case 'progress':
            // Show generation progress
            setProgress(data.tokens_generated);
            break;
            
          case 'done':
            // Finalize with actual metrics
            setFinalMetrics({
              totalTokens: data.total_tokens,
              traceId: data.trace_id
            });
            break;
        }
      }
    }
  }
};
```

## React Components

### Model Selection Indicator
```tsx
interface ModelInfoProps {
  model: string;
  provider: string;
  reasoning: string;
  cost: number;
}

const ModelSelectionIndicator: React.FC<ModelInfoProps> = ({
  model, provider, reasoning, cost
}) => {
  return (
    <div className="model-info">
      <div className="model-badge">
        <span className="model-name">{model}</span>
        <span className="provider">via {provider}</span>
      </div>
      <div className="cost-indicator">
        Est. ${cost.toFixed(4)}
      </div>
      <Tooltip content={reasoning}>
        <InfoIcon />
      </Tooltip>
    </div>
  );
};
```

### Capability Selector
```tsx
interface CapabilitySelectorProps {
  selected: string[];
  onChange: (capabilities: string[]) => void;
}

const CapabilitySelector: React.FC<CapabilitySelectorProps> = ({
  selected, onChange
}) => {
  const [capabilities, setCapabilities] = useState([]);
  
  useEffect(() => {
    // Fetch available capabilities
    fetch('/api/chat/capabilities')
      .then(res => res.json())
      .then(data => setCapabilities(data.capabilities));
  }, []);

  return (
    <div className="capability-selector">
      <h3>AI Capabilities</h3>
      {capabilities.map((cap) => (
        <label key={cap.name} className="capability-option">
          <input
            type="checkbox"
            checked={selected.includes(cap.name)}
            onChange={(e) => {
              if (e.target.checked) {
                onChange([...selected, cap.name]);
              } else {
                onChange(selected.filter(c => c !== cap.name));
              }
            }}
          />
          <span className="capability-name">{cap.name}</span>
          <span className="capability-desc">{cap.description}</span>
        </label>
      ))}
    </div>
  );
};
```

### Cost Tracker
```tsx
const CostTracker: React.FC = () => {
  const [sessionCost, setSessionCost] = useState(0);
  const [requestHistory, setRequestHistory] = useState([]);

  const trackCost = (cost: number, model: string) => {
    setSessionCost(prev => prev + cost);
    setRequestHistory(prev => [...prev, {
      timestamp: new Date(),
      cost,
      model
    }]);
  };

  return (
    <div className="cost-tracker">
      <div className="session-total">
        Session Total: ${sessionCost.toFixed(4)}
      </div>
      <div className="cost-breakdown">
        {requestHistory.map((req, idx) => (
          <div key={idx} className="cost-item">
            <span>{req.model}</span>
            <span>${req.cost.toFixed(4)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Enhanced Composer Integration

### Writer Type with Capabilities
```tsx
const WriterTypeSelect: React.FC = () => {
  const writerTypes = [
    {
      id: 'essay',
      name: 'Academic Essay', 
      capabilities: ['creative_writing', 'reasoning', 'long_context'],
      description: 'Uses high-quality models for academic writing'
    },
    {
      id: 'research',
      name: 'Research Paper',
      capabilities: ['web_search', 'reasoning', 'long_context'],
      description: 'Includes real-time research and citations'
    },
    {
      id: 'code',
      name: 'Code Analysis',
      capabilities: ['code_generation', 'reasoning', 'function_calling'],
      description: 'Optimized for programming tasks'
    }
  ];

  return (
    <Select onValueChange={(value) => {
      const type = writerTypes.find(t => t.id === value);
      setSelectedCapabilities(type?.capabilities || []);
    }}>
      {writerTypes.map(type => (
        <SelectItem key={type.id} value={type.id}>
          <div className="writer-type-option">
            <span className="name">{type.name}</span>
            <span className="description">{type.description}</span>
            <div className="capabilities">
              {type.capabilities.map(cap => (
                <Badge key={cap} variant="secondary">{cap}</Badge>
              ))}
            </div>
          </div>
        </SelectItem>
      ))}
    </Select>
  );
};
```

## Admin Interface Integration

### Model Policy Dashboard
```tsx
const ModelPolicyDashboard: React.FC = () => {
  const [policies, setPolicies] = useState({});
  const [assignments, setAssignments] = useState({});
  const [health, setHealth] = useState(null);

  useEffect(() => {
    // Load gateway status
    Promise.all([
      fetch('/api/admin/gateway/policies').then(r => r.json()),
      fetch('/api/admin/gateway/assignments').then(r => r.json()),
      fetch('/api/admin/gateway/health').then(r => r.json())
    ]).then(([policiesData, assignmentsData, healthData]) => {
      setPolicies(policiesData);
      setAssignments(assignmentsData.assignments);
      setHealth(healthData);
    });
  }, []);

  return (
    <div className="admin-dashboard">
      <GatewayHealthStatus health={health} />
      <ModelAssignmentsTable 
        assignments={assignments}
        policies={policies}
        onUpdate={handlePolicyUpdate}
      />
      <CostOptimizationPanel />
    </div>
  );
};
```

### Real-time Monitoring
```tsx
const TraceMonitor: React.FC = () => {
  const [traces, setTraces] = useState([]);
  
  useEffect(() => {
    const interval = setInterval(async () => {
      const response = await fetch('/api/admin/gateway/traces?limit=20');
      const data = await response.json();
      setTraces(data.traces);
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="trace-monitor">
      <h3>Recent LLM Requests</h3>
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>Node</th>
            <th>Model</th>
            <th>Duration</th>
            <th>Cost</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {traces.map(trace => (
            <tr key={trace.trace_id}>
              <td>{new Date(trace.spans[0]?.start_time).toLocaleTimeString()}</td>
              <td>{trace.spans[0]?.metadata?.node}</td>
              <td>{trace.spans[0]?.metadata?.model}</td>
              <td>{trace.total_duration_ms}ms</td>
              <td>${trace.spans[0]?.metadata?.cost_usd?.toFixed(4)}</td>
              <td className={`status-${trace.spans[0]?.status}`}>
                {trace.spans[0]?.status}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

## Migration Notes

### Backward Compatibility
The new endpoints maintain backward compatibility:
- `/api/chat/send` still works but uses capability inference
- Legacy `mode` parameter maps to capability hints
- Existing streaming format is enhanced, not replaced

### Progressive Enhancement
1. **Phase 1**: Update to new endpoints for enhanced features
2. **Phase 2**: Add capability selection UI components  
3. **Phase 3**: Implement cost tracking and monitoring
4. **Phase 4**: Add admin model management interface

### Environment Variables
Add to your `.env.local`:
```bash
# Enable enhanced features
NEXT_PUBLIC_GATEWAY_V2_ENABLED=true
NEXT_PUBLIC_SHOW_MODEL_SELECTION=true
NEXT_PUBLIC_SHOW_COST_TRACKING=true
NEXT_PUBLIC_ENABLE_CAPABILITY_HINTS=true
```

## Error Handling

```typescript
const handleGatewayError = (error: any) => {
  if (error.detail?.includes('budget')) {
    showToast('Daily budget exceeded. Please try again tomorrow.', 'warning');
  } else if (error.detail?.includes('rate limit')) {
    showToast('Too many requests. Please wait a moment.', 'warning');
  } else if (error.detail?.includes('model selection')) {
    showToast('No suitable AI model available. Try different capabilities.', 'error');
  } else {
    showToast('AI service temporarily unavailable.', 'error');
  }
};
```

This integration maintains your existing UX while adding powerful new capabilities for model optimization and cost management.