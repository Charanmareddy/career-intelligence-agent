"""
Curated Role Profiles for Designation Benchmark Matching
=========================================================

IMPORTANT: These profiles represent general market expectations for the Indian
tech hiring market as of 2025-2026, targeting fresh graduates and early-career
professionals (0-3 years experience). They are reviewed and versioned by the
platform team.

Profiles are stored as Python dicts and loaded into RoleProfile objects at
import time. Update the 'version' field whenever skill expectations change.

Target Roles (7):
  1. ai_engineer      — AI / ML Engineer
  2. ml_engineer      — Machine Learning Engineer
  3. data_scientist   — Data Scientist
  4. genai_engineer   — Generative AI Engineer
  5. python_developer — Python Developer / Backend Engineer
  6. software_engineer — Software Development Engineer (SDE)
  7. data_analyst     — Data Analyst

Assumption common to all profiles:
  - Entry-to-mid level (0-3 years experience range)
  - India tech market (product companies, service companies, startups)
  - 2025-2026 technology landscape
"""

from typing import Dict
from app.schemas.designation_matching import RoleProfile


_ROLE_PROFILE_DICTS: Dict[str, dict] = {

    "ai_engineer": {
        "role_id": "ai_engineer",
        "display_name": "AI / ML Engineer",
        "version": "1.1",
        "description": (
            "Builds, trains, and deploys machine learning models and AI-powered systems "
            "in production. Works across the ML lifecycle: data preprocessing, model training, "
            "evaluation, serving, and monitoring."
        ),
        "mandatory_skills": [
            "Python", "Machine Learning", "Deep Learning", "NumPy", "Pandas",
            "Scikit-learn", "TensorFlow", "PyTorch", "SQL", "Git"
        ],
        "preferred_skills": [
            "MLflow", "Hugging Face", "FastAPI", "Docker", "Kubernetes",
            "LangChain", "LLM", "Feature Engineering", "A/B Testing",
            "AWS", "GCP", "Azure", "REST API", "Data Pipelines"
        ],
        "minimum_experience_years": 0.0,
        "preferred_experience_years": 1.5,
        "domain_knowledge": [
            "Model Deployment", "Model Monitoring", "Feature Stores",
            "Experiment Tracking", "MLOps", "Distributed Training"
        ],
        "education_signals": [
            "Computer Science", "Artificial Intelligence", "Machine Learning",
            "Data Science", "Electronics", "Mathematics", "Statistics"
        ],
        "assumptions": [
            "Entry-to-mid level profile targeting 0-2 years experience candidates.",
            "Assumes Python as the primary programming language.",
            "Both TensorFlow and PyTorch listed; knowing either one is sufficient.",
            "Cloud platform experience (AWS/GCP/Azure) is preferred but not mandatory for freshers.",
            "Based on Indian product company and startup hiring patterns (2025-2026)."
        ]
    },

    "ml_engineer": {
        "role_id": "ml_engineer",
        "display_name": "Machine Learning Engineer",
        "version": "1.0",
        "description": (
            "Focuses on the engineering side of ML: building scalable training pipelines, "
            "model serving infrastructure, and integrating ML models into production applications. "
            "Bridges data science and software engineering."
        ),
        "mandatory_skills": [
            "Python", "Machine Learning", "Scikit-learn", "Pandas", "NumPy",
            "SQL", "REST API", "Git", "Linux"
        ],
        "preferred_skills": [
            "PyTorch", "TensorFlow", "MLflow", "Airflow", "Spark",
            "Docker", "Kubernetes", "FastAPI", "Redis", "PostgreSQL",
            "Feature Engineering", "Model Serving", "CI/CD", "AWS", "GCP"
        ],
        "minimum_experience_years": 0.0,
        "preferred_experience_years": 2.0,
        "domain_knowledge": [
            "ML Pipelines", "Model Serving", "Data Engineering",
            "ETL", "Model Versioning", "Distributed Computing"
        ],
        "education_signals": [
            "Computer Science", "Software Engineering", "Data Science",
            "Machine Learning", "Mathematics", "Statistics"
        ],
        "assumptions": [
            "Profile emphasizes engineering and infrastructure over pure research/modeling.",
            "Assumes candidate should be comfortable building and maintaining data pipelines.",
            "Linux/shell proficiency expected for deployment and debugging tasks.",
            "Based on Indian mid-size product company hiring (2025-2026)."
        ]
    },

    "data_scientist": {
        "role_id": "data_scientist",
        "display_name": "Data Scientist",
        "version": "1.0",
        "description": (
            "Extracts actionable insights from structured and unstructured data. "
            "Applies statistical modeling, machine learning, and data visualization "
            "to drive business decisions. Works closely with product and business teams."
        ),
        "mandatory_skills": [
            "Python", "Statistics", "Machine Learning", "Pandas", "NumPy",
            "Scikit-learn", "SQL", "Data Visualization", "Git"
        ],
        "preferred_skills": [
            "R", "Matplotlib", "Seaborn", "Plotly", "Tableau", "Power BI",
            "Deep Learning", "NLP", "Time Series", "A/B Testing",
            "Hypothesis Testing", "Jupyter", "Spark", "BigQuery", "Airflow"
        ],
        "minimum_experience_years": 0.0,
        "preferred_experience_years": 1.5,
        "domain_knowledge": [
            "Exploratory Data Analysis", "Statistical Hypothesis Testing",
            "Feature Engineering", "Business Intelligence", "Predictive Modeling",
            "Experiment Design"
        ],
        "education_signals": [
            "Data Science", "Statistics", "Mathematics", "Computer Science",
            "Economics", "Physics", "Engineering"
        ],
        "assumptions": [
            "Profile targets analytics-focused data science roles rather than pure ML engineering.",
            "SQL proficiency is mandatory — most DS roles require data extraction skills.",
            "Visualization tools (Tableau or Power BI) strongly preferred in Indian market.",
            "Statistics/math background carries more weight in DS vs ML Engineer roles.",
            "Based on Indian tech/analytics company hiring (2025-2026)."
        ]
    },

    "genai_engineer": {
        "role_id": "genai_engineer",
        "display_name": "Generative AI Engineer",
        "version": "1.1",
        "description": (
            "Designs and builds LLM-powered applications, RAG systems, and AI agents. "
            "Works with foundation models, prompt engineering, vector databases, "
            "and AI orchestration frameworks to create production GenAI products."
        ),
        "mandatory_skills": [
            "Python", "LLM", "Prompt Engineering", "LangChain",
            "OpenAI API", "Gemini API", "REST API", "Git"
        ],
        "preferred_skills": [
            "RAG", "Vector Database", "Pinecone", "ChromaDB", "Weaviate",
            "LangGraph", "Semantic Kernel", "Hugging Face", "FastAPI",
            "LlamaIndex", "Embeddings", "Fine-tuning", "RLHF",
            "Function Calling", "Tool Use", "MCP", "Agents", "Docker"
        ],
        "minimum_experience_years": 0.0,
        "preferred_experience_years": 1.0,
        "domain_knowledge": [
            "Transformer Architecture", "Tokenization", "Context Windows",
            "Retrieval-Augmented Generation", "Agentic Workflows",
            "AI Safety", "Hallucination Mitigation"
        ],
        "education_signals": [
            "Computer Science", "Artificial Intelligence", "Machine Learning",
            "Data Science", "Natural Language Processing", "Software Engineering"
        ],
        "assumptions": [
            "Fast-evolving field; profile reflects 2025-2026 market expectations.",
            "Knowing at least one LLM provider API (OpenAI or Gemini) is mandatory.",
            "LangChain listed as mandatory due to widespread adoption; LlamaIndex is equivalent.",
            "Experience with vector DBs (even in personal projects) significantly improves score.",
            "Fine-tuning and RLHF are preferred but not required at entry level.",
            "Rapidly growing demand in Indian startup and product company ecosystem."
        ]
    },

    "python_developer": {
        "role_id": "python_developer",
        "display_name": "Python Developer / Backend Engineer",
        "version": "1.0",
        "description": (
            "Builds scalable backend services, REST APIs, and microservices using Python. "
            "Works with web frameworks, databases, and cloud infrastructure to deliver "
            "reliable server-side applications."
        ),
        "mandatory_skills": [
            "Python", "REST API", "FastAPI", "SQL", "PostgreSQL",
            "Git", "OOP", "Linux"
        ],
        "preferred_skills": [
            "Django", "Flask", "SQLAlchemy", "Celery", "Redis",
            "Docker", "Kubernetes", "AWS", "GCP", "CI/CD",
            "Unit Testing", "Pytest", "JWT", "OAuth", "Microservices",
            "Async Programming", "WebSockets", "Message Queues", "RabbitMQ", "Kafka"
        ],
        "minimum_experience_years": 0.0,
        "preferred_experience_years": 1.5,
        "domain_knowledge": [
            "API Design", "Database Optimization", "Caching Strategies",
            "Authentication & Authorization", "Scalability Patterns",
            "Service-Oriented Architecture"
        ],
        "education_signals": [
            "Computer Science", "Software Engineering", "Information Technology",
            "Electronics and Communication"
        ],
        "assumptions": [
            "FastAPI listed as mandatory due to dominance in modern Python backend development.",
            "Django and Flask listed as preferred for candidates from older stacks.",
            "PostgreSQL assumed as primary database; MySQL/MongoDB are reasonable equivalents.",
            "Linux proficiency expected for any backend developer role.",
            "Based on Indian product company and startup backend hiring (2025-2026)."
        ]
    },

    "software_engineer": {
        "role_id": "software_engineer",
        "display_name": "Software Development Engineer (SDE)",
        "version": "1.0",
        "description": (
            "Designs, develops, and maintains software systems across the full stack or backend. "
            "Applies strong computer science fundamentals: algorithms, data structures, "
            "system design, and software engineering best practices."
        ),
        "mandatory_skills": [
            "Python", "Data Structures", "Algorithms", "SQL", "REST API",
            "Git", "OOP", "Problem Solving"
        ],
        "preferred_skills": [
            "Java", "C++", "JavaScript", "TypeScript", "React", "Node.js",
            "System Design", "Docker", "Kubernetes", "AWS", "Linux",
            "Microservices", "CI/CD", "Unit Testing", "Design Patterns",
            "PostgreSQL", "MongoDB", "Redis", "Message Queues"
        ],
        "minimum_experience_years": 0.0,
        "preferred_experience_years": 1.5,
        "domain_knowledge": [
            "System Design", "Scalability", "Distributed Systems",
            "Software Development Lifecycle", "Agile Methodologies",
            "Code Review", "Technical Documentation"
        ],
        "education_signals": [
            "Computer Science", "Software Engineering", "Information Technology",
            "Electronics", "B.Tech", "B.E."
        ],
        "assumptions": [
            "Broad profile — covers SDE-1 and SDE-2 equivalent roles.",
            "Python listed as mandatory (widely tested in Indian SDE interviews).",
            "DSA proficiency critical for interview performance at Indian product companies.",
            "System design skills weighted as preferred for fresher/entry-level.",
            "Full-stack and backend specializations both captured under this profile.",
            "Based on Indian tech company SDE hiring patterns (2025-2026)."
        ]
    },

    "data_analyst": {
        "role_id": "data_analyst",
        "display_name": "Data Analyst",
        "version": "1.0",
        "description": (
            "Transforms raw data into actionable business insights using SQL, "
            "spreadsheets, and data visualization tools. Partners with business "
            "teams to define metrics, build dashboards, and communicate findings."
        ),
        "mandatory_skills": [
            "SQL", "Excel", "Data Visualization", "Python", "Pandas"
        ],
        "preferred_skills": [
            "Tableau", "Power BI", "Looker", "Google Analytics",
            "Matplotlib", "Seaborn", "Statistics", "Hypothesis Testing",
            "BigQuery", "Snowflake", "ETL", "Airflow", "R",
            "Dashboard Design", "A/B Testing", "Google Sheets"
        ],
        "minimum_experience_years": 0.0,
        "preferred_experience_years": 1.0,
        "domain_knowledge": [
            "Business Intelligence", "KPI Metrics", "Cohort Analysis",
            "Funnel Analysis", "Data Storytelling", "Stakeholder Reporting"
        ],
        "education_signals": [
            "Data Science", "Statistics", "Mathematics", "Economics",
            "Business Administration", "Computer Science", "Commerce"
        ],
        "assumptions": [
            "SQL is mandatory — no SQL means not qualified for most analyst roles.",
            "Excel proficiency expected even in technical analyst roles.",
            "Python/Pandas listed as mandatory due to growing expectation in Indian market.",
            "Tableau or Power BI strongly preferred — one of them expected for mid-level.",
            "This profile leans towards business/product analytics, not data engineering.",
            "Based on Indian analyst role hiring in e-commerce, fintech, and SaaS (2025-2026)."
        ]
    },
}


def load_all_role_profiles() -> Dict[str, RoleProfile]:
    """
    Load and validate all curated role profiles.

    Returns:
        Dict mapping role_id → RoleProfile (Pydantic validated objects).

    Raises:
        ValidationError: If any profile dict fails Pydantic validation.
    """
    return {
        role_id: RoleProfile.model_validate(profile_dict)
        for role_id, profile_dict in _ROLE_PROFILE_DICTS.items()
    }


# Module-level singleton — loaded once at import time
ROLE_PROFILES: Dict[str, RoleProfile] = load_all_role_profiles()

# Ordered list of available role IDs (for display)
AVAILABLE_ROLE_IDS: list[str] = list(ROLE_PROFILES.keys())
