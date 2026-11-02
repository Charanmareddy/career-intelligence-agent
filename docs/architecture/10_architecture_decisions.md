# 10. Architecture Decision Records (ADR)

## ADR 001: Strict Two-Phase Boundary
- **Context**: Autonomous agents can introduce unpredictable behavior and latency into deterministic operations like document parsing and ATS scoring.
- **Decision**: Phase 1 is strictly non-agentic. All Phase 1 modules (resume parsing, ATS readiness scoring, JD matching) run as deterministic Python pipelines with targeted Gemini structured extractions. Autonomous LangGraph agents are introduced exclusively in Phase 2.
- **Consequence**: Guaranteed testability, predictable latency, explainable scoring, zero agent sprawl.

## ADR 002: Streamlit + FastAPI Separation
- **Context**: Streamlit's reactive rerun model is great for UI prototyping but prone to state leaks and unsuitable for persistent background task orchestration.
- **Decision**: Keep Streamlit strictly as a REST client communicating with FastAPI. No direct DB access, secrets, or Celery task calls in Streamlit code.
- **Consequence**: Backend remains clean, modular, and reusable if frontend is later migrated to React or mobile.

## ADR 003: Gemini Official SDK & Structured Generation
- **Context**: Complex LLM frameworks frequently obscure prompt formatting, introduce breaking interface churn, and add unnecessary token overhead.
- **Decision**: Use the official `google-genai` SDK with Pydantic response schemas for deterministic JSON parsing. Reserve LangChain/LangGraph strictly for multi-step agent graphs and memory in Phase 2.
- **Consequence**: Highly reliable JSON output, lower library weight, and clear type-checked payloads.

## ADR 004: FastMCP for Tool Providers
- **Context**: Multi-agent workflows need standardized access to external job APIs, email dispatchers, and document generators without hardcoding bespoke tool wrappers.
- **Decision**: Build modular FastMCP servers for Job Discovery, Notifications, Document Generation, and Application Integration. Backend acts as MCP client.
- **Consequence**: Tool definitions remain decoupled, testable, and reusable across both automated tasks and interactive agents.

## ADR 005: Grounded Application Generation & Approval Checkpoints
- **Context**: LLMs hallucinate metrics and experience when tailoring resumes or letters.
- **Decision**: Every tailoring prompt strictly pulls approved candidate ground truth from `resume_evidence`. Hallucinated or unverifiable claims fail validation. No application can be submitted externally without explicit, logged user consent.
- **Consequence**: Absolute candidate integrity and ethical safety.
