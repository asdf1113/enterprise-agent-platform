# Implementation Plan

## 1. Purpose

This document defines the implementation roadmap for the Enterprise Agent Platform.

The objective is to convert the frozen Stage 0 design into a sequence of executable engineering milestones while maintaining a balance between:

- Technical depth
- Implementation speed
- Resume value
- Agent engineering learning
- Solution / FDE portfolio value

The implementation strategy follows one core rule:

> Build the project through vertical slices rather than completing isolated modules one by one.

Every milestone must leave the repository in a runnable state and add at least one complete user-facing capability.

---

## 2. Implementation Strategy

The project will not be developed in this order:

```text
Finish all Agent code
↓
Finish all RAG code
↓
Finish all Tool code
↓
Integrate at the end
```

Instead, every milestone follows:

```text
User Request
↓
API
↓
Agent Runtime
↓
Real Capability
↓
Real Data
↓
Answer / Action
↓
Test
↓
Evaluation
```

This ensures that:

- Integration problems appear early
- The main branch remains runnable
- Each milestone produces demonstrable value
- Evaluation evolves with implementation
- Resume-ready capability is reached quickly

---

## 3. Milestone Overview

| Milestone | Goal | Estimated Time | Outcome |
|---|---|---:|---|
| M0 | Repository & Infrastructure Bootstrap | 0.5-1 day | Stable engineering foundation |
| M1 | Agent Runtime MVP | 1.5-2 days | First complete Agent execution loop |
| M2 | Enterprise RAG | 2-3 days | Knowledge retrieval capability |
| M3 | Business Data Agent | 2-3 days | Structured business-data capability |
| M4 | Multi-tool Planning | 2-3 days | Full Agentic workflow |
| Gate A | Resume-ready | ~10-14 days | Suitable for Agent / AI application roles |
| M5 | Security + HITL + MCP | 2-3 days | Enterprise integration and safety |
| M6 | Evaluation + Observability Hardening | 2-3 days | Quantifiable enterprise PoC |
| M7 | Deployment + Benchmark + Solution Package | 3-5 days | FDE-ready portfolio |
| Gate B | FDE-ready | ~3-4 weeks | Solution / FDE presentation-ready |

---

# 4. M0 — Repository & Infrastructure Bootstrap

## 4.1 Goal

Create a stable project foundation before implementing Agent behavior.

Initial repository structure:

```text
enterprise-agent-platform/

├── apps/
│   ├── api/
│   └── web/
├── agent/
├── tools/
├── rag/
├── models/
├── storage/
├── security/
├── data/
├── evaluation/
├── tests/
├── infra/
├── docs/
├── pyproject.toml
├── .env.example
├── .gitignore
└── README.md
```

The Stage 0 documents should be placed under:

```text
docs/

├── 00_customer_brief.md
├── 01_product_requirements.md
├── 02_agent_workflow.md
├── 03_system_architecture.md
├── 04_data_design.md
├── 05_evaluation_plan.md
└── 06_implementation_plan.md
```

---

## 4.2 Technology Baseline

| Area | Decision |
|---|---|
| Python | 3.11 |
| Dependency Management | pyproject.toml + uv |
| API | FastAPI |
| Data Validation | Pydantic v2 |
| Configuration | pydantic-settings |
| Agent Runtime | LangGraph |
| LLM Client | OpenAI Python SDK |
| Database | PostgreSQL |
| Database Access | SQLAlchemy 2 |
| PostgreSQL Driver | psycopg |
| Vector Storage | pgvector |
| SQL Parsing | sqlglot |
| Embedding | BGE-M3 |
| Reranker | BGE reranker |
| Testing | pytest |
| Containerization | Docker Compose |

The OpenAI SDK is used through an OpenAI-compatible interface so the Model Gateway can later connect to:

- Cloud providers
- Qwen-compatible endpoints
- vLLM
- SGLang

---

## 4.3 Explicitly Deferred Infrastructure

Do not introduce at M0:

- Redis
- Kafka
- Milvus
- Kubernetes
- Prometheus
- Grafana

These are not required for the initial PoC.

---

## 4.4 Definition of Done

M0 is complete when:

```bash
docker compose up -d
```

successfully starts PostgreSQL.

The project test framework runs:

```bash
pytest
```

The API exposes:

```text
GET /health
```

and returns:

```json
{
  "status": "ok"
}
```

---

# 5. M1 — Agent Runtime MVP

## 5.1 Goal

Build the first complete Agent execution lifecycle.

The initial graph:

```text
START
↓
request_parser
↓
router
↓
tool execution
↓
synthesizer
↓
END
```

M1 intentionally excludes:

- RAG
- Planner
- Long-term memory
- HITL
- MCP

---

## 5.2 Initial State

Implement only the state fields currently required:

```python
class AgentState(TypedDict):
    request_id: str
    thread_id: str
    user_id: str
    role: str
    messages: list
    query: str
    task_type: str | None
    tool_calls: list
    tool_results: list
    error: str | None
    final_answer: str | None
```

Additional fields from `02_agent_workflow.md` are introduced only when later milestones require them.

---

## 5.3 Initial Tool

Use a real business-oriented tool instead of throw-away demo functionality.

Initial capability:

```text
get_product_info(product_name)
```

This tool reads the PostgreSQL `products` table.

Example request:

```text
查询X200的基础产品信息
```

Execution:

```text
FastAPI
↓
LangGraph
↓
Router
↓
get_product_info
↓
PostgreSQL
↓
LLM
↓
Answer
```

---

## 5.4 Main Files

```text
apps/api/main.py
apps/api/routes/chat.py
apps/api/schemas/chat.py

agent/state.py
agent/graph.py
agent/router.py
agent/nodes/

models/gateway.py

tools/business_data.py

storage/database.py

tests/test_agent_graph.py
tests/test_business_tool.py
```

---

## 5.5 Definition of Done

The API supports:

```text
POST /chat
```

Example input:

```json
{
  "user_id": "u001",
  "role": "sales",
  "thread_id": "demo-1",
  "message": "查询X200的基础产品信息"
}
```

The execution must produce:

```text
Router
↓
Tool
↓
Database
↓
LLM
↓
Answer
```

The response includes:

```json
{
  "answer": "...",
  "trace_id": "..."
}
```

The trace records:

- route
- tool call
- tool result
- latency

At this point the Agent Runtime skeleton is considered valid.

---

# 6. M2 — Enterprise RAG

## 6.1 Goal

Add the enterprise knowledge capability through RAG.

Architecture:

```text
Agent Runtime
↓
Knowledge Tool
↓
RAG Pipeline
```

The system does not create a separate autonomous “RAG Agent.”

---

## 6.2 Ingestion Pipeline

Implement:

```text
Document
↓
Parser
↓
Chunking
↓
Embedding
↓
pgvector
```

The initial dataset should contain only:

```text
5-10 documents
```

This keeps iteration fast while validating the entire pipeline.

---

## 6.3 Retrieval Pipeline

Implement:

```text
Query
↓
BGE-M3
↓
Vector Search Top-20
↓
ACL / Metadata Filter
↓
Reranker
↓
Top-5 Evidence
```

Initial values are configurable and will later be tuned through evaluation.

---

## 6.4 Citation

Every knowledge answer must expose evidence.

Example:

```text
X200标准保修期为3年。

Source:
X200 Product Manual
Section 4.2 Warranty
```

Citation support is part of the M2 definition of done.

---

## 6.5 Graph Extension

The graph becomes:

```text
                 router
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
 product/data             knowledge
        │                     │
        │              knowledge_search
        │                     │
        └──────────┬──────────┘
                   ▼
              synthesizer
```

This milestone introduces a meaningful LangGraph Conditional Edge.

---

## 6.6 Main Files

```text
rag/
├── ingestion.py
├── parser.py
├── chunking.py
├── embedding.py
├── vectorstore.py
├── retriever.py
└── reranker.py

tools/knowledge.py

agent/nodes/knowledge.py

data/documents/

tests/test_retriever.py
tests/test_knowledge_workflow.py
```

---

## 6.7 Evaluation

Create:

```text
evaluation/dataset/knowledge.json
```

Initial size:

```text
10-15 tasks
```

Measure:

- Recall@5
- Citation Accuracy

Evaluation begins here rather than being postponed to the end.

---

## 6.8 Definition of Done

A user can ask a knowledge question through the API and receive:

- Correct routed workflow
- Retrieved evidence
- Reranked context
- Grounded final answer
- Citation

Automated retrieval tests and initial evaluation results must be available.

---

# 7. M3 — Business Data Agent

## 7.1 Goal

Add natural-language business-data querying.

Workflow:

```text
User
↓
Router
↓
Data Workflow
↓
LLM Structured SQL Request
↓
SQL Guard
↓
PostgreSQL
↓
Structured Result
↓
LLM Explanation
```

---

## 7.2 Business Data Generation

Implement the synthetic environment defined in `04_data_design.md`.

Target scale:

```text
customers     ~1,000
products      ~50-100
orders        ~50,000
sales         ~50,000
tickets       ~10,000
```

Controlled business patterns must be encoded.

Core Hero Workflow pattern:

```text
South China Q1:
X200 sales relatively strong

South China Q2:
X200 sales decrease materially

Policy:
Q2 X200 incentives become weaker
```

This creates explainable ground truth for later complex analysis.

---

## 7.3 SQL Generation

The LLM should return structured output.

Example:

```json
{
  "sql": "SELECT ...",
  "reason": "需要计算2026 Q2华南销售总额"
}
```

The SQL is never executed before validation.

---

## 7.4 SQL Guard

Implement with `sqlglot`.

Required checks:

- SELECT only
- table allowlist
- no DDL
- no UPDATE / DELETE / INSERT
- row limit
- timeout
- read-only database role

The guard must be implemented independently from the LLM prompt.

---

## 7.5 Evaluation

Create:

```text
evaluation/dataset/data_query.json
```

Initial size:

```text
15-20 deterministic tasks
```

Measure:

- SQL Execution Success Rate
- Result Accuracy
- SQL Safety Compliance

Do not compare exact SQL strings.

Compare the actual query result against ground truth.

---

## 7.6 Definition of Done

The user can ask natural-language business questions and receive correct data-driven answers through:

```text
NL Query
↓
Structured SQL
↓
SQL Guard
↓
PostgreSQL
↓
Result
↓
Explanation
```

Unsafe queries must be blocked.

---

# 8. M4 — Multi-tool Planning

## 8.1 Goal

Upgrade the platform from multiple independent workflows into a genuine Agentic workflow that combines tools dynamically.

This milestone is the core Resume-ready milestone.

---

## 8.2 Plan-and-Execute

Example task:

```text
分析华南Q2销售下降原因，并结合营销政策给出建议。
```

Planner output:

```json
{
  "steps": [
    {
      "tool": "query_business_data",
      "goal": "比较华南Q1和Q2销售数据"
    },
    {
      "tool": "knowledge_search",
      "goal": "检索Q1和Q2营销政策变化"
    },
    {
      "tool": "analyze_data",
      "goal": "识别主要变化因素"
    }
  ]
}
```

Executor behavior:

```text
Step 1
↓
Tool
↓
Observation
↓
State

Step 2
↓
Tool
↓
Observation
↓
State

...

Verifier
↓
Synthesizer
```

---

## 8.3 Analysis Tool

Do not provide arbitrary Python execution.

Expose controlled operations:

```text
group_by
comparison
trend
growth_rate
top_k
```

This improves:

- security
- determinism
- testability

---

## 8.4 Evaluation

Create:

```text
evaluation/dataset/analysis.json
```

Initial size:

```text
~15 tasks
```

Measure:

- Correct Tool Sequence Rate
- Evidence Coverage
- Task Completion Rate

---

## 8.5 Gate A — Resume-ready

The project is considered Resume-ready after M4 when it includes:

```text
FastAPI
+
LangGraph
+
RAG
+
Reranker
+
SQL Agent
+
SQL Guard
+
Multi-tool Planning
+
Evaluation
```

Target stable evaluation set:

```text
>= 50 tasks
```

Suggested initial distribution:

```text
Knowledge       20
Data            15
Complex         15
```

At this stage the project is strong enough to appear on resumes for:

- Agent Engineer
- AI Application Engineer
- LLM Application Engineer

Measured metrics should be added to the resume only after evaluation.

---

# 9. M5 — Security + HITL + MCP

## 9.1 Goal

Upgrade the system from an Agent engineering project into an enterprise-oriented Solution PoC.

---

## 9.2 RBAC

Roles:

```text
sales
support
management
admin
```

Permissions must affect:

- RAG metadata filtering
- SQL data scope
- Tool availability
- Write operations

---

## 9.3 Human-in-the-loop

Example:

```text
User:
给客户A创建高优先级跟进任务

↓

Agent generates action proposal

↓

Graph pauses

↓

Human Approval

↓

Graph resumes

↓

CRM Tool executes

↓

Audit Log
```

This milestone uses LangGraph capabilities such as:

- checkpoint
- interrupt
- resume

---

## 9.4 CRM Integration

First implement a simulated CRM REST API.

Example endpoint:

```text
POST /crm/tickets
```

The Agent accesses it through:

```text
CRM Tool
```

rather than direct service coupling.

---

## 9.5 MCP Integration

After the CRM integration works through the normal Tool interface, add:

```text
Agent
↓
MCP Client
↓
CRM MCP Server
↓
CRM Service
```

MCP is used to standardize enterprise capability exposure, not because Tool Calling itself requires MCP.

---

## 9.6 Definition of Done

The system demonstrates:

- role-aware access
- safe Action workflow
- approval before write execution
- audit trail
- CRM REST integration
- MCP-based connector extension

---

# 10. M6 — Evaluation + Observability Hardening

## 10.1 Goal

Turn milestone-level evaluation into a unified evaluation system.

Final target:

```text
100 tasks
```

Distribution:

| Category | Tasks |
|---|---:|
| Knowledge | 30 |
| Data | 25 |
| Complex Analysis | 25 |
| Action | 10 |
| Security | 10 |

---

## 10.2 Evaluation Runner

Target command:

```bash
python -m evaluation.runner
```

Pipeline:

```text
Load Dataset
↓
Run Agent
↓
Capture Trace
↓
Calculate Metrics
↓
Generate Report
```

Outputs:

```text
evaluation/results/

├── run_YYYYMMDD_HHMMSS.json
└── summary_YYYYMMDD_HHMMSS.md
```

---

## 10.3 Unified Trace

Record:

```text
trace_id
request_id
route
plan
tool_calls
tool_results
retrieved_chunks
citations
latency
tokens
errors
answer
```

At this milestone, a third-party observability platform is optional.

The system should first understand and own its own trace data model.

Possible later integrations:

- LangSmith
- Phoenix
- OpenTelemetry

---

## 10.4 Definition of Done

The evaluation runner can execute the complete suite and produce:

- Quality metrics
- Security metrics
- Latency metrics
- Failure taxonomy
- Raw traces
- Summary report

---

# 11. M7 — Deployment + Benchmark + Solution Package

## 11.1 Goal

Transform the engineering project into an FDE / Solution portfolio artifact.

---

## 11.2 Docker Compose Deployment

Minimum services:

```text
agent-api
postgres
web
```

Target experience:

```bash
docker compose up
```

starts the complete PoC.

---

## 11.3 Local LLM Integration

Connect a local model through:

```text
Model Gateway
↓
vLLM
↓
Local Model
```

The Agent business logic should not change.

Only configuration such as:

```text
MODEL_BASE_URL
MODEL_NAME
```

should change.

This validates the Model Gateway abstraction.

---

## 11.4 Benchmark

Benchmark at least:

- Knowledge tasks
- Data tasks
- Complex tasks

Measure:

```text
P50 latency
P95 latency
token usage
model calls
cost / task
```

Optional comparison:

```text
Cloud Model
vs
Local Model
```

---

## 11.5 Architecture Trade-off Analysis

The final project must be able to explain:

- Why PostgreSQL + pgvector instead of Milvus?
- Why RAG instead of fine-tuning?
- Why simple requests bypass the Planner?
- Why not Multi-Agent?
- Why do write operations require HITL?
- Why can private deployment replace only the Model Gateway backend?
- When would Kubernetes become necessary?
- How would architecture differ for 100 vs 10,000 users?

These decisions should be documented and reflected in the Solution Deck.

---

## 11.6 FDE-ready Deliverables

### Engineering Evidence

```text
GitHub Repository
Automated Tests
Docker Deployment
Agent Platform
```

### System Evidence

```text
Architecture Diagram
Security Design
Deployment Design
```

### Quantitative Evidence

```text
Evaluation Report
Latency Report
Accuracy Metrics
Cost Analysis
```

### Customer-facing Evidence

```text
Customer Brief
Solution Deck
Demo
```

---

# 12. Gate B — FDE-ready

The project becomes FDE-ready when:

- Engineering implementation is reproducible
- Evaluation is measurable
- Security decisions are demonstrated
- Deployment architecture is explainable
- Cost / performance trade-offs are available
- A customer-facing narrative exists

At this point the project should be presented as:

> Enterprise Agent / RAG Solution PoC

rather than merely:

> LangGraph Agent project

---

# 13. Suggested Schedule

For approximately 3-5 focused hours per day:

| Time | Work |
|---|---|
| Day 1 | M0 |
| Day 2-3 | M1 |
| Day 4-6 | M2 |
| Day 7-9 | M3 |
| Day 10-12 | M4 |
| Day 13-15 | Tests, Evaluation, README, Gate A |
| Week 3 | M5 + M6 |
| Week 4 | M7 + Solution Deck |

Expected result:

```text
~2 weeks → Resume-ready
~3-4 weeks → FDE-ready
```

If interview preparation interrupts development, Gate A remains a complete and valuable stopping point.

---

# 14. Definition of Done for Every Milestone

A milestone is complete only when all four conditions are satisfied:

```text
1. Feature
   The capability actually works.

2. Test
   Automated tests pass.

3. Evaluation
   Corresponding evaluation tasks exist.

4. Demo
   A complete user-facing input/output path works.
```

Example:

RAG is not complete merely because embeddings were generated.

It is complete only when:

```text
User Question
↓
Router
↓
RAG
↓
Evidence
↓
Citation
↓
Answer
```

works end-to-end and the project records retrieval metrics.

---

# 15. Git Development Strategy

Each milestone should produce clear commits.

Recommended history:

```text
chore: bootstrap enterprise agent platform

feat(agent): add LangGraph runtime MVP

feat(rag): add enterprise knowledge retrieval workflow

feat(data): add guarded business data query workflow

feat(agent): add plan-and-execute multi-tool analysis

feat(security): add RBAC and human approval workflow

feat(eval): add agent evaluation and tracing framework

feat(deploy): add local serving and solution benchmark
```

The Git history should itself show the system's incremental evolution.

---

# 16. Scope Control

During implementation, new technologies should not be added simply because they are popular.

Examples:

```text
GraphRAG
Hybrid Search
Agent2Agent
CrewAI
Memory Bank
Redis
Kafka
Celery
Kubernetes
Graph Database
```

Default decision:

```text
Do not add.
```

A new technology is introduced only when a concrete requirement or measured limitation justifies it.

Example:

If dense retrieval performs poorly for product identifiers, then evaluate:

```text
BM25 / Hybrid Search
```

rather than introducing Elasticsearch in advance.

The guiding principle is:

> Solve the measured problem instead of expanding the technology stack.

---

# 17. Stage 0 Completion

The complete Stage 0 design chain is:

```text
00 Customer Brief
↓
Why the customer needs the system

01 Product Requirements
↓
What the product must provide

02 Agent Workflow
↓
How the Agent executes tasks

03 System Architecture
↓
How software components implement the workflow

04 Data Design
↓
What data drives the system

05 Evaluation Plan
↓
How system quality is measured

06 Implementation Plan
↓
How the system will be built
```

After this document is frozen, Stage 0 is complete.

Implementation starts with:

```text
M0 — Repository & Infrastructure Bootstrap
```
