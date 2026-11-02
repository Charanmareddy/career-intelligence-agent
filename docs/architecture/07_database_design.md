# 07. Database Design & Entity Relationship

## Database: PostgreSQL + SQLAlchemy 2.0 + Alembic

```mermaid
erDiagram
    USERS ||--o{ CANDIDATE_PROFILES : has
    USERS ||--o{ RESUMES : uploads
    USERS ||--o{ USER_PREFERENCES : configures
    USERS ||--o{ NOTIFICATIONS : receives
    USERS ||--o{ APPLICATIONS : owns

    RESUMES ||--o{ RESUME_EVIDENCE : contains
    RESUMES ||--o{ RESUME_ANALYSIS : analyzed_as

    SCORING_MODELS ||--o{ RESUME_ANALYSIS : versions
    SCORING_MODELS ||--o{ JOB_MATCHES : versions

    ROLE_PROFILES ||--o{ JOB_REQUIREMENTS : defines
    JOB_DESCRIPTIONS ||--o{ JOB_REQUIREMENTS : contains

    JOB_SOURCES ||--o{ JOBS : provides
    JOBS ||--o{ JOB_REQUIREMENTS : contains

    USERS ||--o{ JOB_MATCHES : receives
    JOBS ||--o{ JOB_MATCHES : produces

    JOBS ||--o{ APPLICATIONS : applied_for
    APPLICATIONS ||--o{ APPLICATION_EVENTS : records
    APPLICATIONS ||--o{ GENERATED_DOCUMENTS : uses

    USERS ||--o{ AGENT_RUNS : initiates
    AGENT_RUNS ||--o{ WORKFLOW_CHECKPOINTS : stores
    USERS ||--o{ AUDIT_EVENTS : generates
```

### Table Definitions & Key Constraints
- `users`: UUID primary key, email, hashed credentials, role, status.
- `resumes`: UUID pk, user_id fk, original_filename, stored_filepath, file_hash, file_size, mime_type, created_at.
- `resume_evidence`: UUID pk, resume_id fk, section, item_type, content, metadata_json.
- `resume_analysis`: UUID pk, resume_id fk, scoring_model_id, total_ats_score, breakdown_json, recommendations_json.
- `jobs`: UUID pk, source_id, external_id, title, company, location, is_remote, description, raw_hash, posting_date.
- `job_matches`: UUID pk, user_id fk, job_id fk, match_score, matched_skills_json, missing_skills_json, evidence_map_json.
- `applications`: UUID pk, user_id fk, job_id fk, status (Enum), tailored_resume_id fk, cover_letter_id fk, approved_at.
