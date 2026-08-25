from typing import List, Optional

from pydantic import BaseModel, Field

from .schema import EligibilityRule, FreshnessStatus, Provenance


class StudentProfile(BaseModel):
    age: int = Field(ge=1, le=100)
    state: str = Field(min_length=2, max_length=100)
    education_level: str = Field(min_length=2, max_length=30)
    course: Optional[str] = Field(default=None, max_length=120)
    category: Optional[str] = Field(default=None, max_length=30)
    annual_family_income: Optional[float] = Field(default=None, ge=0)
    gender: Optional[str] = Field(default=None, max_length=30)
    disability: bool = False
    class12_percentile: Optional[float] = Field(default=None, ge=0, le=100)
    regular_course: Optional[bool] = None
    is_diploma: Optional[bool] = None
    gap_after_class12: Optional[bool] = None
    receives_other_scholarship: Optional[bool] = None
    admission_in_qhei: Optional[bool] = None
    working_professional_part_time: Optional[bool] = None


class Scheme(BaseModel):
    id: str
    name: str
    authority: str
    description: str
    scheme_type: str = "scholarship"
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
    official_url: Optional[str] = None
    last_verified: Optional[str] = None
    source: str
    source_page: Optional[str] = None
    source_text: str
    provenance: List[Provenance] = []
    eligibility_rules: List[EligibilityRule] = []
    freshness: Optional[FreshnessStatus] = None
    manual_review_required: bool = False
    manual_review_reason: Optional[str] = None


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
