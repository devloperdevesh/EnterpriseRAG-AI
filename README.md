# EnterpriseRAG-AI

## Observability-First AI Infrastructure Platform

EnterpriseRAG-AI is an observability-driven AI infrastructure platform focused on Retrieval-Augmented Generation (RAG), distributed tracing, semantic retrieval, async orchestration, and scalable backend execution.

The project explores modern infrastructure engineering patterns around request lifecycle visibility, telemetry pipelines, retrieval diagnostics, reliability engineering, streaming systems, and distributed backend architectures.

### Key Metrics

| Metric          | Value                  |
| --------------- | ---------------------- |
| Throughput      | ~850 Requests/sec      |
| p95 Latency     | ~480ms                 |
| Architecture    | Async FastAPI Services |
| Retrieval Layer | FAISS Semantic Search  |
| Cache Layer     | Redis                  |
| Database        | PostgreSQL             |
| Observability   | OpenTelemetry + Jaeger |
| Metrics         | Prometheus + Grafana   |

### Engineering Focus

* Distributed AI Infrastructure
* Retrieval-Augmented Generation
* Async Backend Systems
* Distributed Tracing
* Infrastructure Telemetry
* Streaming Pipelines
* Reliability Engineering
* Performance Optimization
* Semantic Retrieval Systems
* Queue-Oriented Orchestration

📈 Detailed performance reports, latency analysis, throughput benchmarks, and infrastructure diagnostics:

**[View Performance Benchmarks](./PERFORMANCE_BENCHMARKS.md)**



# Infrastructure Vision

EnterpriseRAG AI is evolving toward an infrastructure-oriented AI systems engineering platform where retrieval workflows, request execution pipelines, distributed traces, and streaming inference systems are fully observable and visually explorable.

The long-term engineering direction focuses on:

* realtime retrieval diagnostics
* request lifecycle visibility
* distributed observability workflows
* infrastructure telemetry pipelines
* queue-driven execution systems
* streaming-aware inference orchestration
* scalable semantic retrieval infrastructure
* backend reliability experimentation
* infrastructure debugging workflows
* AI systems instrumentation

---

# Current Development Status

| Infrastructure Area                  | Status              |
| ------------------------------------ | ------------------- |
| Landing Page Infrastructure UI       | Completed           |
| Async Backend Architecture           | In Progress         |
| Semantic Retrieval Pipeline          | Prototype           |
| Observability Instrumentation        | Partial Integration |
| Realtime Streaming Infrastructure    | In Progress         |
| Infrastructure Metrics Dashboard     | Under Development   |
| Distributed Tracing Workflows        | Experimental        |
| Queue-Oriented Execution Systems     | Planned             |
| Reliability Engineering Workflows    | Planned             |
| Kubernetes Deployment Infrastructure | Planned             |

---

# Core Engineering Focus Areas

## Distributed Retrieval Infrastructure

EnterpriseRAG AI experiments with distributed retrieval execution workflows involving:

* semantic chunk retrieval
* vector similarity search
* retrieval latency instrumentation
* context assembly pipelines
* retrieval diagnostics
* async retrieval execution
* retrieval observability workflows
* realtime retrieval telemetry

---

## Observability-Driven Backend Systems

The platform heavily emphasizes infrastructure observability and backend visibility across the request lifecycle.

Current observability exploration areas include:

* OpenTelemetry instrumentation
* Jaeger distributed tracing
* Prometheus metrics aggregation
* Grafana infrastructure visualization
* request execution diagnostics
* latency analytics
* streaming-aware instrumentation
* infrastructure telemetry pipelines
* queue execution visibility
* backend workflow tracing

---

## Streaming Infrastructure Workflows

EnterpriseRAG AI explores realtime streaming infrastructure workflows focused on:

* SSE/WebSocket streaming
* token-level streaming visibility
* stream lifecycle diagnostics
* latency-aware streaming pipelines
* concurrent stream handling
* realtime infrastructure events
* streaming observability systems
* async stream orchestration

---

# High-Level Architecture

```text
                         ┌─────────────────────────┐
                         │ Client Applications     │
                         │ Web • Dashboard • APIs  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ NGINX Gateway Layer     │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ FastAPI Async Services  │
                         └────────────┬────────────┘
                                      │
          ┌───────────────┬────────────┼────────────┬───────────────┐
          ▼               ▼            ▼            ▼
   ┌───────────┐   ┌───────────┐ ┌───────────┐ ┌────────────┐
   │ Redis     │   │ FAISS     │ │ PostgreSQL│ │ Celery     │
   │ Cache     │   │ Retrieval │ │ Database  │ │ Workers    │
   └─────┬─────┘   └─────┬─────┘ └─────┬─────┘ └─────┬──────┘
         │               │             │             │
         └───────────────┴─────────────┴─────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Context Assembly Layer  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ LLM Execution Pipeline  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ Streaming Response Bus  │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │ OpenTelemetry Tracing   │
                         └────────────┬────────────┘
                                      │
                                      ▼
                   ┌──────────────────────────────────────┐
                   │ Jaeger • Prometheus • Grafana        │
                   └──────────────────────────────────────┘
```

---

# Request Lifecycle Visibility

EnterpriseRAG AI is being designed around complete request lifecycle instrumentation.

The platform aims to visualize:

```text
User Query
    ↓
Embedding Generation
    ↓
Semantic Retrieval
    ↓
Chunk Ranking
    ↓
Context Assembly
    ↓
LLM Inference
    ↓
Realtime Streaming
    ↓
Trace Generation
    ↓
Metrics Aggregation
```

This infrastructure-oriented workflow visibility is one of the primary engineering goals of the platform.

---

# Planned Infrastructure Visualizations

## Retrieval Workflow Visualization

Interactive retrieval diagnostics showing:

* semantic chunk boundaries
* retrieval rankings
* similarity scores
* context injection workflows
* retrieval latency metrics
* embedding relationships
* query execution diagnostics

---

## Distributed Trace Explorer

Infrastructure trace visualization focused on:

* request spans
* backend execution stages
* latency breakdowns
* queue wait times
* streaming execution visibility
* distributed trace correlation
* infrastructure bottleneck diagnostics

---

## Streaming Observability Dashboard

Realtime streaming analytics focused on:

* token streaming metrics
* stream lifecycle diagnostics
* concurrent stream visibility
* latency instrumentation
* websocket activity monitoring
* realtime infrastructure events

---

# Engineering Roadmap

| Area                       | Planned Work                                           | Status      |
| -------------------------- | ------------------------------------------------------ | ----------- |
| Retrieval Visualization    | Interactive retrieval workflow visualization dashboard | Planned     |
| Chunk Diagnostics          | Semantic chunk debugger and retrieval explorer         | Planned     |
| Request Lifecycle Explorer | Full request execution visualization                   | Planned     |
| Streaming Infrastructure   | SSE/WebSocket streaming observability                  | In Progress |
| Distributed Tracing        | Trace explorer and latency analytics                   | In Progress |
| Metrics Infrastructure     | Retrieval throughput and latency instrumentation       | In Progress |
| Reliability Engineering    | Retry orchestration and replay workflows               | Planned     |
| Queue Infrastructure       | Queue-aware async execution systems                    | Planned     |
| Infrastructure Monitoring  | Expanded Prometheus and Grafana telemetry              | Planned     |
| Kubernetes Workflows       | Scalable deployment infrastructure                     | Planned     |
| Backend Diagnostics        | Infrastructure failure analysis tooling                | Planned     |
| AI Systems Instrumentation | Advanced telemetry pipelines for retrieval systems     | Planned     |
| Event Streaming Infrastructure | Apache Kafka Integration | Planned |

---

# Contribution Areas

Contributions are welcome across:

* observability dashboards
* infrastructure visualization systems
* realtime streaming workflows
* distributed tracing integrations
* retrieval diagnostics
* queue orchestration workflows
* backend reliability tooling
* infrastructure telemetry systems
* developer tooling improvements
* frontend infrastructure engineering
* AI systems instrumentation
* infrastructure monitoring workflows

---

# Open Source Engineering Direction

EnterpriseRAG AI is being developed as an engineering-oriented open-source platform focused on infrastructure experimentation and backend systems learning.

The project prioritizes:

* practical backend engineering
* infrastructure visibility
* observability-first architectures
* scalable retrieval workflows
* distributed systems experimentation
* async infrastructure patterns
* contributor collaboration
* engineering-focused OSS workflows

Rather than positioning itself as a finished enterprise platform, the repository focuses on exploring scalable infrastructure concepts involved in modern AI systems engineering.

---

# Technology Stack

## Backend Infrastructure

- FastAPI
- Redis
- PostgreSQL
- SQLAlchemy
- FAISS
- Celery

### Planned Infrastructure

- Apache Kafka (Event Streaming)
- Queue Buffer Mesh
- Event-Driven Processing Pipelines

## Frontend Infrastructure

* React
* TypeScript
* Recharts

## Observability Stack

* OpenTelemetry
* Jaeger
* Prometheus
* Grafana

## Infrastructure & Deployment

* Docker
* NGINX
* Railway
* Vercel
* Kubernetes (Planned)

---

# Local Development Setup

## Prerequisites

Install the following:

* Python 3.11+
* Node.js 18+
* Git
* Docker Desktop

---

# Clone Repository

```bash
git clone https://github.com/devloperdevesh/EnterpriseRAG-AI.git

cd EnterpriseRAG-AI
```

---

# Infrastructure Setup (Docker)

EnterpriseRAG uses PostgreSQL and Redis for local development.

Start the infrastructure services:

```bash
docker compose up -d postgres redis
```

Verify containers are running:

```bash
docker ps
```

Expected containers:

```text
postgres_enterprise_rag
redis_enterprise_rag
```

Default local services:

| Service    | Port |
| ---------- | ---- |
| PostgreSQL | 5432 |
| Redis      | 6379 |

---

# Backend Setup

Navigate to the backend directory:

```bash
cd app
```

Create virtual environment:

### Windows

```bash
python -m venv venv

venv\Scripts\activate
```

### Linux / macOS

```bash
python -m venv venv

source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements/base.txt

pip install -r requirements/dev.txt
```

---

# Environment Configuration

Create a `.env` file inside the backend directory:

```env
APP_NAME=EnterpriseRAG

SECRET_KEY=change-me

ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=60

DATABASE_URL=postgresql://postgres:password@localhost:5432/enterprise_rag

REDIS_URL=redis://localhost:6379/0
```

---

# Run Backend

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Swagger Documentation:

```text
http://127.0.0.1:8000/docs
```

---

# Frontend Setup

Open a new terminal.

Navigate to frontend:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Run development server:

```bash
npm run dev
```

Frontend:

```text
http://localhost:5173
```

---

# Full Infrastructure Stack (Optional)

To start all available services:

```bash
docker compose up -d
```

This may include:

* PostgreSQL
* Redis
* Grafana
* Prometheus
* Backend Services (when configured)

Stop all services:

```bash
docker compose down
```

---

# Current Development Features

Implemented:

* User Authentication
* JWT-based Authorization
* Document Upload Pipeline
* PDF Processing
* Semantic Chunking
* Embedding Generation
* FAISS Vector Storage
* React Dashboard Interface

Under Active Development:

* Infrastructure Observability
* Metrics Visualization
* Distributed Tracing
* Streaming Workflows
* Reliability Engineering Features
* Retrieval Diagnostics


# Engineering Areas Explored

* distributed systems engineering
* async backend infrastructure
* semantic retrieval systems
* realtime streaming workflows
* observability-first architectures
* distributed tracing systems
* infrastructure telemetry pipelines
* queue-driven orchestration
* reliability engineering workflows
* infrastructure diagnostics
* scalable AI backend experimentation
* retrieval infrastructure instrumentation

---

# Open Source Collaboration

EnterpriseRAG AI actively encourages contributor collaboration around:

* RAG infrastructure visualization
* streaming observability
* infrastructure monitoring
* backend telemetry workflows
* distributed tracing systems
* retrieval optimization
* async infrastructure engineering
* developer experience tooling
* observability-first backend systems

---

## Devesh Chauhan

Backend Systems Engineer focused on Distributed Systems, Observability, AI Infrastructure, and Scalable Backend Architectures.

- Project Admin & Mentor, GSSoC
- Open Source Contributor
- Distributed Systems & AI Infrastructure Enthusiast
