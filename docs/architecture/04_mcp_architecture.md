# 04. Model Context Protocol (MCP) Architecture

## Role of MCP Servers
MCP servers are stateless, typed tool providers using FastMCP / Python MCP SDK.
They **never** act as autonomous agents; they expose controlled capabilities to LangGraph agents and FastAPI services.

```mermaid
flowchart TB
    subgraph BACKEND["FastAPI / LangGraph Agents"]
        AGENT[LangGraph Agent Context]
        MCP_MGR[MCP Client Manager]
        AGENT --> MCP_MGR
    end

    subgraph SERVERS["FastMCP Custom Servers"]
        S1[Job Discovery MCP Server]
        S2[Notification MCP Server]
        S3[Document Generation MCP Server]
        S4[Application Integration MCP Server]
    end

    MCP_MGR --> S1
    MCP_MGR --> S2
    MCP_MGR --> S3
    MCP_MGR --> S4

    subgraph TARGETS["External Integrations & Core Services"]
        E1[Adzuna / Career API Feeds]
        E2[Email SMTP / In-App DB Alerts]
        E3[python-docx / PDF Engine]
        E4[Authorized ATS Forms / URL Dispatch]
    end

    S1 --> E1
    S2 --> E2
    S3 --> E3
    S4 --> E4
```

### Server Boundaries and Responsibilities
1. **Job Discovery Server**: Exposes `search_jobs`, `get_job_details`, `get_company_jobs`. Rate-limited, cached.
2. **Notification Server**: Exposes `send_email_notification`, `send_job_match_alert`. Enforces deduplication and user notification frequency caps.
3. **Document Generation Server**: Exposes `generate_tailored_resume`, `generate_cover_letter`, `export_resume_pdf`. Reuses python-docx templates.
4. **Application Integration Server**: Exposes `prepare_application`, `submit_application` (strictly requiring cryptographic user approval token).
