# Enterprise Agent Platform

An enterprise-oriented Agent platform for knowledge retrieval, business data analysis, and controlled business workflow automation.

## Business Problem

Enterprise employees often need to work across multiple disconnected information sources:

- internal knowledge documents,
- product manuals and policies,
- structured business databases,
- CRM / ERP systems.

Traditional workflows require manual document search, SQL support from data teams, and repeated cross-system coordination.

This project explores how an enterprise Agent runtime can connect these capabilities through controlled, observable, and evaluable workflows.

## Solution Overview

The platform is designed around:

- FastAPI application layer
- LangGraph Agent runtime
- enterprise RAG
- guarded business-data tools
- Plan-and-Execute workflows
- Human-in-the-loop actions
- evaluation and observability
- cloud and private LLM deployment through a Model Gateway

## Current Status

Stage 0 architecture and planning are complete.

Current implementation milestone:

**M0 — Repository & Infrastructure Bootstrap**

## Architecture

Detailed design documents are available under:

```text
docs/
Development

The project uses:

Python 3.11
uv
FastAPI
PostgreSQL
pgvector
Docker Compose

Run tests:

uv run pytest

Start PostgreSQL:

docker compose -f infra/docker-compose.yml up -d

Run API:

uv run uvicorn apps.api.main:app --reload

