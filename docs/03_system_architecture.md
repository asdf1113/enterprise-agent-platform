# System Architecture Design

## 1. Overview

This document defines the software architecture of the Enterprise Agent
Platform.

The architecture converts business requirements and Agent workflows into
an implementable enterprise AI system.

The system contains:

-   Application Layer
-   Agent Runtime Layer
-   Tool / Capability Layer
-   Data and Knowledge Layer
-   Model Layer
-   Evaluation and Observability Layer

The design principles are:

1.  Separate reasoning workflow from external capabilities.
2.  Use controlled tools instead of direct system access.
3.  Keep model providers replaceable.
4.  Build evaluation and observability into the system.

------------------------------------------------------------------------

# 2. High-Level Architecture

    User
     |
    Web / API Client
     |
    FastAPI Gateway
     |
    Agent Runtime (LangGraph)
     |
    +----------------------+----------------------+
    |                      |                      |
    Knowledge Tool      Data Tool          Action Tool
    |                      |                      |
    RAG System       Business Database    Enterprise API
     |
    Model Gateway
     |
    +----------------+
    |                |
    Cloud LLM      vLLM
     |
    Evaluation & Observability

------------------------------------------------------------------------

# 3. Application Layer

## FastAPI Gateway

Directory:

    apps/api/

Responsibilities:

-   Receive requests
-   Authentication
-   Session management
-   Streaming responses
-   API routing

The Web interface is separated from backend logic.

Directory:

    apps/web/

Purpose:

-   Demo interface
-   Agent execution visualization
-   Solution presentation

------------------------------------------------------------------------

# 4. Agent Runtime Layer

Directory:

    agent/

Implemented with LangGraph.

Responsibilities:

-   Workflow execution
-   State transition
-   Routing
-   Planning
-   Tool orchestration
-   Response synthesis

Main components:

    graph.py
    state.py
    router.py
    planner.py
    executor.py
    nodes/

The runtime follows:

    State -> Node -> Updated State

------------------------------------------------------------------------

# 5. Tool / Capability Layer

Directory:

    tools/

Tools expose controlled enterprise capabilities.

Common interface:

    name
    description
    input schema
    execute()

## Knowledge Tool

Provides:

-   Document retrieval
-   Evidence extraction
-   Citation generation

## Business Data Tool

Provides:

-   Natural language data query
-   SQL execution
-   Result formatting

Security:

-   Read-only database
-   SQL validation
-   Table allowlist

## Analysis Tool

Provides:

-   Aggregation
-   Comparison
-   Trend analysis

## CRM Action Tool

Provides:

-   Business operation execution
-   Human approval
-   Audit records

------------------------------------------------------------------------

# 6. Knowledge System

Directory:

    rag/

Pipeline:

    Document
     |
    Parser
     |
    Chunking
     |
    Embedding
     |
    Vector Store
     |
    Retriever
     |
    Reranker
     |
    Context
     |
    LLM

Technology:

-   Embedding: BGE-M3
-   Vector Store: PostgreSQL + pgvector

Reason:

-   Simple deployment
-   Metadata filtering
-   Suitable for PoC scale

------------------------------------------------------------------------

# 7. Business Data Layer

Example data:

    customers
    products
    orders
    sales
    tickets

Workflow:

    User Query

    ↓

    Agent

    ↓

    SQL Tool

    ↓

    SQL Validator

    ↓

    Database

    ↓

    Result Explanation

Direct unrestricted SQL execution is prohibited.

------------------------------------------------------------------------

# 8. Enterprise Integration Layer

Enterprise systems are accessed through adapters.

Example:

    Agent

    ↓

    Adapter

    ↓

    CRM / ERP / Ticket System

Future MCP extension:

    Agent

    ↓

    MCP Client

    ↓

    MCP Server

    ↓

    Enterprise API

MCP is considered an integration standard, not the Agent core.

------------------------------------------------------------------------

# 9. Model Gateway

Directory:

    models/

Purpose:

Abstract model providers.

Interface:

    chat()
    stream()
    embedding()

Supported modes:

## Cloud Mode

    Agent -> Gateway -> Cloud API

## Private Deployment

    Agent -> Gateway -> vLLM -> GPU

------------------------------------------------------------------------

# 10. Storage Layer

Directory:

    storage/

Contains:

## Database

PostgreSQL stores:

-   Business data
-   User information
-   Configuration

## Memory

Stores:

-   Conversation history
-   Session information

Implementation:

-   LangGraph checkpoint
-   Persistent storage

## Vector Storage

Stores:

-   Document embeddings
-   Metadata

------------------------------------------------------------------------

# 11. Security Layer

Directory:

    security/

Components:

## Authentication

Controls:

-   User identity
-   Session verification

## Tool Policy

Controls:

-   Available tools
-   Permission scope

## SQL Guard

Controls:

-   SELECT only
-   Table whitelist
-   Query limitation
-   Timeout

------------------------------------------------------------------------

# 12. Evaluation and Observability

Directory:

    evaluation/

Evaluation flow:

    Dataset

    ↓

    Agent Runner

    ↓

    Trace

    ↓

    Metrics

    ↓

    Report

Metrics:

## RAG

-   Recall@K
-   Citation Accuracy

## Agent

-   Routing Accuracy
-   Tool Success Rate
-   Task Completion Rate

## System

-   Latency
-   Token Usage
-   Cost

Observability records:

-   Request
-   Routing decision
-   Plan
-   Tool calls
-   Tool latency
-   Retrieved evidence
-   Errors
-   Final answer

------------------------------------------------------------------------

# 13. Deployment Architecture

## MVP

    User

    ↓

    FastAPI

    ↓

    Agent Runtime

    ↓

    PostgreSQL + LLM API

## Production-oriented

    User

    ↓

    Load Balancer

    ↓

    API Services

    ↓

    Agent Runtime

    ↓

    Model Gateway

    ↓

    vLLM / Cloud API

------------------------------------------------------------------------

# 14. Repository Mapping

    enterprise-agent-platform/

    ├── apps/
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
    └── docs/

------------------------------------------------------------------------

# 15. Future Extensions

-   MCP enterprise connectors
-   Long-term memory
-   Multi-tenant architecture
-   Advanced monitoring
-   Kubernetes deployment
-   Distributed inference service
