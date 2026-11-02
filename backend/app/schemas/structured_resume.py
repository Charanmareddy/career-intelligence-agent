from typing import List, Optional
from pydantic import BaseModel, Field

class ContactInformation(BaseModel):
    full_name: str = Field(description="Candidate's full name")
    email: Optional[str] = Field(default=None, description="Email address")
    phone: Optional[str] = Field(default=None, description="Phone / mobile number")
    location: Optional[str] = Field(default=None, description="City, State/Province, Country")
    linkedin_url: Optional[str] = Field(default=None, description="LinkedIn profile URL")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    portfolio_url: Optional[str] = Field(default=None, description="Personal website or portfolio URL")

class SkillsInventory(BaseModel):
    languages: List[str] = Field(default_factory=list, description="Programming languages (e.g. Python, SQL, C++)")
    frameworks_and_libraries: List[str] = Field(default_factory=list, description="Frameworks (e.g. FastAPI, PyTorch, React)")
    databases: List[str] = Field(default_factory=list, description="Databases (e.g. PostgreSQL, Redis, MongoDB)")
    cloud_and_devops: List[str] = Field(default_factory=list, description="Cloud/DevOps (e.g. AWS, Docker, Git, Kubernetes)")
    ai_ml_tools: List[str] = Field(default_factory=list, description="AI/ML tools (e.g. LangGraph, Hugging Face, Scikit-Learn)")
    developer_tools: List[str] = Field(default_factory=list, description="Tools and IDEs (e.g. VS Code, Postman, JIRA)")
    soft_skills: List[str] = Field(default_factory=list, description="Identifiable soft skills (e.g. Agile, Team Leadership)")

class WorkExperienceItem(BaseModel):
    job_title: str = Field(description="Role or title held")
    company: str = Field(description="Company or organization name")
    location: Optional[str] = Field(default=None, description="Location of work")
    start_date: Optional[str] = Field(default=None, description="Start date (e.g., Jun 2022 or 2022)")
    end_date: Optional[str] = Field(default=None, description="End date or 'Present'")
    is_current: bool = Field(default=False, description="Whether this is the current job")
    responsibilities_and_achievements: List[str] = Field(default_factory=list, description="Bullet points detailing achievements and metrics")
    technologies_used: List[str] = Field(default_factory=list, description="Specific technologies mentioned in this role")

class ProjectItem(BaseModel):
    project_title: str = Field(description="Title of project")
    description: str = Field(description="Brief overview of project purpose and architecture")
    role: Optional[str] = Field(default=None, description="Candidate's role in the project")
    technologies_used: List[str] = Field(default_factory=list, description="Technologies, libraries, and frameworks used")
    project_url: Optional[str] = Field(default=None, description="GitHub repo or live URL if available")
    key_outcomes: List[str] = Field(default_factory=list, description="Measured results, performance gains, or accomplishments")

class EducationItem(BaseModel):
    institution: str = Field(description="University, College, or School name")
    degree: str = Field(description="Degree name (e.g. B.Tech, M.S., B.S.)")
    field_of_study: Optional[str] = Field(default=None, description="Major / Specialization (e.g. Computer Science)")
    start_year: Optional[str] = Field(default=None, description="Starting year")
    graduation_year: Optional[str] = Field(default=None, description="Graduation year or expected graduation year")
    grade_or_gpa: Optional[str] = Field(default=None, description="GPA or percentage if stated")

class CertificationItem(BaseModel):
    name: str = Field(description="Certification title")
    issuing_organization: str = Field(description="Issuing organization (e.g. AWS, Google Cloud, Coursera)")
    issue_date: Optional[str] = Field(default=None, description="Issue date")
    credential_id: Optional[str] = Field(default=None, description="Credential ID or license number")
    credential_url: Optional[str] = Field(default=None, description="Verification URL")

class StructuredResume(BaseModel):
    contact_info: ContactInformation
    professional_summary: Optional[str] = Field(default=None, description="Professional executive summary or objective")
    skills: SkillsInventory = Field(default_factory=SkillsInventory)
    work_experience: List[WorkExperienceItem] = Field(default_factory=list)
    internships: List[WorkExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list, description="Awards, honors, or competitive accomplishments")
    publications: List[str] = Field(default_factory=list, description="Research papers or articles")
    extraction_notes: List[str] = Field(default_factory=list, description="Notations or ambiguity flags noticed during extraction")
