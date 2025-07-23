# Architecture

## Mermaid Flow

```mermaid
graph TD
    A[User] -->|Sends Prompt & Files| B(Frontend);
    B -->|tus-js-client| C(Tus Upload);
    C -->|S3| D[Storage];
    B -->|POST /api/chat| E(Backend);
    E -->|JWT Validation| F(Security Middleware);
    F -->|Tiered Routing| G(API Handler);
    G -->|Creates trace_id| H(DB);
    G -->|Selects Graph| I(YAML Config);
    G -->|Instantiates Nodes| J(Node Objects);
    E -->|Returns trace_id| B;
    B -->|WebSocket| K(NodeRunner);
    K -->|Executes Nodes| L(Agent Nodes);
    L -->|LLM Calls| M(Model Service);
    M -->|Budget Guard| N(Budget Check);
    N -->|Degraded?| O{Emit budget_degraded};
    O --> K;
    L -->|File Processing| P(Celery Workers);
    P -->|Chunking| Q(Chunk Splitter);
    Q -->|Embedding| R(Embedding Service);
    R -->|Vector Storage| S(Vector DB);
    L -->|Derivatives| T(Celery Workers);
    T -->|Turnitin, Slides, etc.| U(External APIs);
    U -->|WebSocket| B;
