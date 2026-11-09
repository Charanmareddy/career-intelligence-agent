"""
Phase 1 Evaluation Dataset: Synthetic Benchmark Resumes
=========================================================

Five standardized, synthetic candidate profiles used to validate and benchmark:
1. ATS Readiness Scoring Engine
2. Job Description Matching Engine
3. Designation Benchmark Matching Engine

The profiles cover diverse career stages and quality levels:
- Profile 1: STRONG_AI_ENGINEER (Senior / Competitive, high metrics, complete)
- Profile 2: MODERATE_PYTHON_DEV (Mid-level, missing metrics, moderate completeness)
- Profile 3: WEAK_SPARSE_CANDIDATE (Sparse, unformatted, poor achievement phrasing)
- Profile 4: FRESH_GRAD_DATA_SCIENTIST (0 years formal exp, strong projects & degrees)
- Profile 5: EXPERIENCED_BACKEND_ARCHITECT (7+ years exp, enterprise architecture, leadership)
"""

from app.schemas.resume import DocumentExtractionResult, DocumentMetadata
from app.schemas.structured_resume import (
    StructuredResume,
    ContactInformation,
    SkillsInventory,
    WorkExperienceItem,
    ProjectItem,
    EducationItem,
    CertificationItem,
)


def get_strong_ai_engineer() -> tuple[DocumentExtractionResult, StructuredResume]:
    """Strong profile with high ATS completeness, quantified metrics, modern tech stack."""
    resume = StructuredResume(
        contact_info=ContactInformation(
            full_name="Aarav Sharma",
            email="aarav.sharma@example.com",
            phone="+91 9876543210",
            location="Bengaluru, Karnataka, India",
            github_url="https://github.com/aaravsharma-ai",
            linkedin_url="https://linkedin.com/in/aaravsharma-ai",
        ),
        professional_summary=(
            "Results-driven Senior AI Engineer with over 4 years of experience architecting and deploying "
            "deep learning pipelines, multi-agent systems, and scalable REST backends. Proven record of "
            "reducing inference latency by 35% and improving classification accuracy across production NLP services."
        ),
        skills=SkillsInventory(
            languages=["Python", "SQL", "Bash", "C++"],
            frameworks_and_libraries=[
                "PyTorch", "TensorFlow", "Scikit-learn", "Hugging Face", "FastAPI",
                "LangChain", "LangGraph", "NumPy", "Pandas",
            ],
            databases=["PostgreSQL", "Redis", "Pinecone", "ChromaDB"],
            tools=["Docker", "Kubernetes", "Git", "Linux", "MLflow", "Airflow"],
            cloud_and_devops=["AWS", "GCP", "CI/CD GitHub Actions"],
            ai_ml_tools=["PyTorch", "TensorFlow", "Hugging Face", "LangChain", "LangGraph", "MLflow"],
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="Senior AI Engineer",
                company="Synthetix Labs",
                location="Bengaluru, India",
                start_date="Jul 2022",
                end_date="Present",
                is_current=True,
                responsibilities_and_achievements=[
                    "Architected high-throughput RAG systems processing 2.5M queries monthly with 99.9% uptime.",
                    "Optimized Transformer inference latency by 42% utilizing ONNX runtime and TensorRT quantization.",
                    "Led a cross-functional squad of 5 engineers to deliver multi-tenant FastAPI inference microservices.",
                ],
                skills_used=["Python", "PyTorch", "FastAPI", "Docker", "AWS", "LangGraph"],
            ),
            WorkExperienceItem(
                job_title="Machine Learning Engineer",
                company="DataVanguard Technologies",
                location="Hyderabad, India",
                start_date="Jun 2020",
                end_date="Jun 2022",
                is_current=False,
                responsibilities_and_achievements=[
                    "Engineered end-to-end customer churn prediction pipelines yielding 18% improvement in retention.",
                    "Automated daily ETL pipelines using Apache Airflow and PostgreSQL handling 500GB daily log volume.",
                    "Mentored 3 junior data scientists and established unit testing standards using Pytest.",
                ],
                skills_used=["Python", "Scikit-learn", "SQL", "Airflow", "PostgreSQL"],
            ),
        ],
        projects=[
            ProjectItem(
                project_title="Enterprise Semantic Search Engine",
                description="Engineered vector search engine over 10M internal technical documents.",
                technologies_used=["Python", "Pinecone", "FastAPI", "Docker", "Hugging Face"],
                role="Lead Architect",
            ),
            ProjectItem(
                project_title="Distributed Model Evaluation Framework",
                description="Created automated benchmarking tool running regression tests on LLM outputs.",
                technologies_used=["Python", "Pytest", "PostgreSQL", "Redis"],
                role="Author",
            ),
        ],
        education=[
            EducationItem(
                institution="National Institute of Technology (NIT) Karnataka",
                degree="B.Tech",
                field_of_study="Computer Science and Engineering",
                graduation_year="2020",
                cgpa_or_percentage="8.9 / 10 CGPA",
            )
        ],
        certifications=[
            CertificationItem(
                name="AWS Certified Machine Learning - Specialty",
                issuing_organization="Amazon Web Services",
                issue_date="2023",
            )
        ],
    )

    doc_result = DocumentExtractionResult(
        document_id="eval-doc-strong-ai",
        success=True,
        raw_text="Aarav Sharma Senior AI Engineer Python PyTorch FastAPI AWS Docker ...",
        cleaned_text=(
            "Aarav Sharma | Senior AI Engineer | Bengaluru\n"
            "Summary: Results-driven Senior AI Engineer with over 4 years of experience.\n"
            "Skills: Python, PyTorch, FastAPI, Docker, AWS, PostgreSQL, Redis, LangGraph.\n"
            "Experience: Synthetix Labs, DataVanguard Technologies.\n"
            "Education: NIT Karnataka B.Tech Computer Science."
        ),
        metadata=DocumentMetadata(
            filename="aarav_sharma_strong.pdf",
            file_extension=".pdf",
            file_size_bytes=45000,
            page_count=2,
            character_count=3200,
            sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            word_count=520,
        ),
    )
    return doc_result, resume


def get_moderate_python_developer() -> tuple[DocumentExtractionResult, StructuredResume]:
    """Moderate profile: decent technical skills but unquantified bullet points and missing summary."""
    resume = StructuredResume(
        contact_info=ContactInformation(
            full_name="Priya Nair",
            email="priya.nair@example.com",
            phone="+91 9123456789",
            location="Pune, India",
        ),
        professional_summary="Python Developer with experience in web backends and SQL databases.",
        skills=SkillsInventory(
            languages=["Python", "SQL", "JavaScript"],
            frameworks_and_libraries=["Django", "Flask", "Pandas"],
            databases=["PostgreSQL", "SQLite"],
            tools=["Git", "Postman"],
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="Software Developer",
                company="SoftSolutions India",
                start_date="Jan 2023",
                end_date="Present",
                is_current=True,
                responsibilities_and_achievements=[
                    "Responsible for developing backend REST APIs using Django framework.",
                    "Worked on database queries and fixed bugs reported by QA team.",
                    "Helped the senior engineer with user authentication modules.",
                ],
                skills_used=["Python", "Django", "PostgreSQL"],
            )
        ],
        projects=[
            ProjectItem(
                project_title="Task Management System",
                description="Built a web application for tracking office tasks.",
                technologies_used=["Python", "Django", "SQLite"],
            )
        ],
        education=[
            EducationItem(
                institution="Pune University",
                degree="B.E.",
                field_of_study="Information Technology",
                graduation_year="2022",
            )
        ],
    )

    doc_result = DocumentExtractionResult(
        document_id="eval-doc-mod-python",
        success=True,
        raw_text="Priya Nair Software Developer Python Django PostgreSQL Git ...",
        cleaned_text=(
            "Priya Nair | Python Developer | Pune\n"
            "Skills: Python, Django, PostgreSQL, Git, JavaScript.\n"
            "Experience: SoftSolutions India. Developed backend REST APIs.\n"
            "Education: Pune University B.E. Information Technology."
        ),
        metadata=DocumentMetadata(
            filename="priya_nair_moderate.pdf",
            file_extension=".pdf",
            file_size_bytes=28000,
            page_count=1,
            character_count=1450,
            sha256_hash="a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
            word_count=210,
        ),
    )
    return doc_result, resume


def get_weak_sparse_candidate() -> tuple[DocumentExtractionResult, StructuredResume]:
    """Weak profile: sparse, first-person pronouns, no quantified metrics, missing sections."""
    resume = StructuredResume(
        contact_info=ContactInformation(
            full_name="Candidate Three",
            email="candidate3@example.com",
        ),
        professional_summary="I am a hardworking person seeking a good software job in a reputed company.",
        skills=SkillsInventory(
            languages=["Python"],
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="Helper Developer",
                company="Local Agency",
                start_date="2023",
                end_date="2023",
                is_current=False,
                responsibilities_and_achievements=[
                    "I handled daily tasks assigned by my manager.",
                    "I attended meetings and checked code.",
                ],
                skills_used=["Python"],
            )
        ],
        projects=[],
        education=[],
    )

    doc_result = DocumentExtractionResult(
        document_id="eval-doc-weak-sparse",
        success=True,
        raw_text="Candidate Three I am a hardworking person Python ...",
        cleaned_text=(
            "Candidate Three\n"
            "I am a hardworking person seeking a good software job.\n"
            "Skills: Python.\n"
            "Experience: Local Agency Helper Developer."
        ),
        metadata=DocumentMetadata(
            filename="weak_resume.pdf",
            file_extension=".pdf",
            file_size_bytes=12000,
            page_count=1,
            character_count=450,
            sha256_hash="00112233445566778899aabbccddeeff00112233445566778899aabbccddeeff",
            word_count=65,
        ),
    )
    return doc_result, resume


def get_fresh_grad_data_scientist() -> tuple[DocumentExtractionResult, StructuredResume]:
    """Fresh graduate profile: 0 full-time years, but strong academic projects, internships, and coursework."""
    resume = StructuredResume(
        contact_info=ContactInformation(
            full_name="Rohan Kulkarni",
            email="rohan.kulkarni@example.com",
            phone="+91 9988001122",
            location="Bengaluru, India",
            github_url="https://github.com/rohan-ds",
        ),
        professional_summary=(
            "Enthusiastic Data Science graduate with hands-on internship experience building predictive "
            "ML models in Python, Scikit-learn, and Pandas. Passionate about applying statistical modeling "
            "and exploratory data analysis to solve complex business problems."
        ),
        skills=SkillsInventory(
            languages=["Python", "SQL", "R"],
            frameworks_and_libraries=["Scikit-learn", "Pandas", "NumPy", "Matplotlib", "Seaborn"],
            databases=["MySQL", "PostgreSQL"],
            tools=["Git", "Jupyter", "VS Code", "Tableau"],
            ai_ml_tools=["Scikit-learn", "Pandas", "NumPy"],
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="Data Science Intern",
                company="AnalyticsEdge Solutions",
                start_date="Jan 2024",
                end_date="Jun 2024",
                is_current=False,
                responsibilities_and_achievements=[
                    "Analyzed customer transactional data across 100K+ records using SQL and Pandas.",
                    "Built customer segmentation model using K-Means clustering, identifying 4 distinct buyer personas.",
                    "Created automated weekly reporting dashboards in Tableau for marketing stakeholders.",
                ],
                skills_used=["Python", "SQL", "Pandas", "Scikit-learn", "Tableau"],
            )
        ],
        projects=[
            ProjectItem(
                project_title="Credit Card Fraud Detection System",
                description="Built XGBoost classification model detecting fraudulent credit transactions with 96% recall.",
                technologies_used=["Python", "Scikit-learn", "Pandas", "Matplotlib"],
                role="Individual Project",
            ),
            ProjectItem(
                project_title="COVID-19 Trend Forecasting",
                description="Time series analysis using ARIMA and Prophet to forecast regional case trends.",
                technologies_used=["Python", "Pandas", "Prophet", "Seaborn"],
                role="Academic Capstone",
            ),
        ],
        education=[
            EducationItem(
                institution="Indian Institute of Information Technology (IIIT) Bangalore",
                degree="B.Tech",
                field_of_study="Computer Science and Data Science",
                graduation_year="2024",
                cgpa_or_percentage="8.6 CGPA",
            )
        ],
    )

    doc_result = DocumentExtractionResult(
        document_id="eval-doc-fresh-ds",
        success=True,
        raw_text="Rohan Kulkarni Data Science Graduate Python SQL Scikit-learn Pandas Tableau ...",
        cleaned_text=(
            "Rohan Kulkarni | Data Science Graduate | Bengaluru\n"
            "Summary: Enthusiastic Data Science graduate with hands-on internship experience.\n"
            "Skills: Python, SQL, R, Scikit-learn, Pandas, NumPy, Tableau, Git.\n"
            "Internship: AnalyticsEdge Solutions Data Science Intern.\n"
            "Projects: Credit Card Fraud Detection, COVID-19 Trend Forecasting.\n"
            "Education: IIIT Bangalore B.Tech Data Science."
        ),
        metadata=DocumentMetadata(
            filename="rohan_kulkarni_fresher.pdf",
            file_extension=".pdf",
            file_size_bytes=36000,
            page_count=1,
            character_count=2350,
            sha256_hash="11223344556677889900aabbccddeeff11223344556677889900aabbccddeeff",
            word_count=380,
        ),
    )
    return doc_result, resume


def get_experienced_backend_architect() -> tuple[DocumentExtractionResult, StructuredResume]:
    """Experienced profile: 8 years experience, system design, microservices, cloud, high architectural scope."""
    resume = StructuredResume(
        contact_info=ContactInformation(
            full_name="Vikramaditya Rao",
            email="vikram.rao@example.com",
            phone="+91 9811223344",
            location="Hyderabad, India",
            linkedin_url="https://linkedin.com/in/vikram-rao-architect",
        ),
        professional_summary=(
            "Principal Software Engineer and Backend Architect with over 8 years of experience "
            "designing fault-tolerant distributed systems, high-throughput microservices, and database "
            "clusters serving 15M+ active users. Deep expertise in Python, FastAPI, PostgreSQL, and Kubernetes."
        ),
        skills=SkillsInventory(
            languages=["Python", "Go", "SQL", "Bash"],
            frameworks_and_libraries=["FastAPI", "Django", "SQLAlchemy", "Celery"],
            databases=["PostgreSQL", "Redis", "Cassandra", "MongoDB"],
            tools=["Docker", "Kubernetes", "Git", "Terraform", "Kafka", "RabbitMQ"],
            cloud_and_devops=["AWS", "GCP", "CI/CD", "Prometheus", "Grafana"],
        ),
        work_experience=[
            WorkExperienceItem(
                job_title="Principal Backend Architect",
                company="FinGlobal Cloud Services",
                start_date="Mar 2021",
                end_date="Present",
                is_current=True,
                responsibilities_and_achievements=[
                    "Spearheaded redesign of payments core into event-driven microservices processing $4B annual volume.",
                    "Engineered distributed caching layer with Redis clusters, reducing DB load by 60%.",
                    "Architected automated failover strategy across multiple AWS regions with sub-second recovery.",
                ],
                skills_used=["Python", "FastAPI", "PostgreSQL", "Redis", "Kafka", "AWS", "Kubernetes"],
            ),
            WorkExperienceItem(
                job_title="Lead Software Engineer",
                company="HyperScale Networks",
                start_date="Jun 2016",
                end_date="Feb 2021",
                is_current=False,
                responsibilities_and_achievements=[
                    "Scaled real-time notification engine from 100K to 10M daily events with Celery and Redis.",
                    "Mentored 12 backend engineers and introduced code review and automated CI/CD gating.",
                ],
                skills_used=["Python", "Django", "PostgreSQL", "Docker", "AWS"],
            ),
        ],
        projects=[
            ProjectItem(
                project_title="High-Throughput API Gateway",
                description="Custom async API gateway with rate limiting, circuit breaker, and JWT authentication.",
                technologies_used=["Python", "FastAPI", "Redis", "Docker"],
            )
        ],
        education=[
            EducationItem(
                institution="BITS Pilani",
                degree="B.E. (Hons)",
                field_of_study="Computer Science",
                graduation_year="2016",
            )
        ],
    )

    doc_result = DocumentExtractionResult(
        document_id="eval-doc-exp-arch",
        success=True,
        raw_text="Vikramaditya Rao Principal Backend Architect Python Go FastAPI PostgreSQL Kubernetes ...",
        cleaned_text=(
            "Vikramaditya Rao | Principal Backend Architect | Hyderabad\n"
            "Summary: Principal Software Engineer with over 8 years of experience.\n"
            "Skills: Python, Go, FastAPI, PostgreSQL, Kubernetes, Redis, Kafka, AWS.\n"
            "Experience: FinGlobal Cloud Services, HyperScale Networks.\n"
            "Education: BITS Pilani B.E. Computer Science."
        ),
        metadata=DocumentMetadata(
            filename="vikram_rao_architect.pdf",
            file_extension=".pdf",
            file_size_bytes=52000,
            page_count=2,
            character_count=3600,
            sha256_hash="fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
            word_count=560,
        ),
    )
    return doc_result, resume


def load_all_evaluation_profiles() -> dict:
    """Returns all 5 benchmark profiles in a structured lookup dictionary."""
    return {
        "strong_ai": get_strong_ai_engineer(),
        "moderate_python": get_moderate_python_developer(),
        "weak_sparse": get_weak_sparse_candidate(),
        "fresh_ds": get_fresh_grad_data_scientist(),
        "experienced_arch": get_experienced_backend_architect(),
    }
