from pydantic import BaseModel, Field
from typing import Optional, List

class StudentProfile(BaseModel):
    age: int = Field(ge=1, le=100)
    state: str
    education_level: str
    course: Optional[str] = None
    category: Optional[str] = None
    annual_family_income: Optional[float] = Field(default=None, ge=0)
    gender: Optional[str] = None
    disability: bool = False

class Scheme(BaseModel):
    id: str
    name: str
    authority: str
    description: str
    state: Optional[str] = None
    education_levels: List[str] = []
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    max_income: Optional[float] = None
    categories: List[str] = []
    genders: List[str] = []
    disability_required: Optional[bool] = None
    benefit: str
    documents: List[str] = []
    application_url: Optional[str] = None
    source: str
    source_page: Optional[str] = None
    source_text: str

class EligibilityResult(BaseModel):
    scheme: Scheme
    status: str
    score: float
    reasons: List[str]
    missing_information: List[str] = []

class RecommendationResponse(BaseModel):
    query: Optional[str] = None
    language: str = "en"
    profile: StudentProfile
    results: List[EligibilityResult]
    disclaimer: str
