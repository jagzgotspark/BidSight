from pydantic import BaseModel
from typing import Optional


class CompanyProfileCreate(BaseModel):
    company_name: str
    services: str
    tech_stack: str = ""
    certifications: str = ""
    team_size: str = "small"
    geography: str = ""
    min_budget: str = "0"
    max_budget: str = "500"


class CompanyProfileResponse(BaseModel):
    id: str
    user_id: str
    company_name: str
    services: str
    tech_stack: str
    certifications: str
    team_size: str
    geography: str
    min_budget: str
    max_budget: str

    class Config:
        from_attributes = True


class MatchScoreResponse(BaseModel):
    tender_id: str
    tender_title: str
    score: int
    reasoning: str
    strengths: list[str]
    risks: list[str]