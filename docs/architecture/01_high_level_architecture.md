# 01. High-Level Architecture

## Architecture Style: Modular Monolith + Hybrid AI & Multi-Agent

```mermaid
flowchart TB
    U[Candidate / User]

    subgraph FRONTEND["Presentation Layer (Streamlit)"]
        S[Streamlit Application]
        P1[Resume Analyzer]
        P2[Job Matcher]
        P3[Job Discovery]
        P4[Notifications]
        P5[Application Tracker]
        P1 --- S
        P2 --- S
        P3 --- S
        P4 --- S
        P5 --- S
    end

    subgraph BACKEND["Backend Layer (FastAPI)"]
        API[FastAPI Gateway]
        AUTH[Authentication & RBAC]
        SERVICES[Python Business Services]
    end

    subgraph AI["AI and Workflow Layer"]
        GEM[Google Gemini API (Official Gen AI SDK)]
        WF[Controlled AI Workflows]
        SCORE[Deterministic Scoring and Matching Engine]
    end

    subgraph AGENTS["Phase 2 Multi-Agent Layer (LangGraph)"]
        ORCH[Career Intelligence Orchestrator Agent]
        JOB[Job Discovery Agent]
        APP[Application Preparation Agent]
    end

    subgraph MCP["MCP Integration Layer"]
        CLIENT[MCP Client Manager]
        JM[Job Discovery MCP Server]
        NM[Notification MCP Server]
        DM[Document Generation MCP Server]
        AM[Application Integration MCP Server]
    end

    subgraph BACKGROUND["Background Processing"]
        BEAT[Celery Beat Scheduler]
        WORKER[Celery Worker Cluster]
        REDIS[Redis Broker & State Cache]
    end

    subgraph STORAGE["Persistence Layer"]
        DB[(PostgreSQL)]
        FILES[Private File Storage]
    end

    subgraph MONITOR["Observability & Testing"]
        LF[Langfuse]
        LOGS[Structured Logs & Metrics]
        TESTS[Pytest Test Suite]
    end

    U --> S
    S --> API
    API --> AUTH
    AUTH --> SERVICES
    SERVICES --> WF
    SERVICES --> SCORE
    WF --> GEM

    SERVICES --> DB
    SERVICES --> FILES

    SERVICES --> ORCH
    ORCH --> JOB
    ORCH --> APP

    JOB --> CLIENT
    APP --> CLIENT
    CLIENT --> JM
    CLIENT --> NM
    CLIENT --> DM
    CLIENT --> AM

    JM --> SERVICES
    NM --> SERVICES
    DM --> SERVICES
    AM --> SERVICES

    BEAT --> REDIS
    REDIS --> WORKER
    WORKER --> SERVICES
    WORKER --> ORCH

    SERVICES --> LF
    ORCH --> LF
    SERVICES --> LOGS
    SERVICES --> TESTS
    WF --> LF
```

## Layer Separation and Boundaries
1. **Presentation Layer**: Streamlit multi-page frontend strictly making REST calls to FastAPI. No direct DB access, secrets, or privileged logic.
2. **Backend API**: FastAPI enforcing JWT/Bearer auth, rate limiting, request validation via Pydantic, and dispatching to services.
3. **Core Services**: Deterministic Python operations for document parsing, scoring equations, deduplication, and database persistence.
4. **AI Workflows**: Gemini 2.5/Flash structured extraction and reasoning with deterministic Pydantic schema enforcement.
5. **Agent Orchestration**: LangGraph state graphs with bounded iterations, scoped tools, and human-in-the-loop checkpoints.
