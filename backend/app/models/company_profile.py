from sqlalchemy import Column, String, DateTime, Text, func
from app.database import Base


class CompanyProfile(Base):
    __tablename__ = "company_profiles"

    id = Column(String, primary_key=True)
    user_id = Column(String, unique=True, nullable=False)

    # What the company does
    company_name = Column(String, default="")
    services = Column(Text, default="")        # comma-separated
    tech_stack = Column(Text, default="")      # comma-separated
    certifications = Column(Text, default="")  # comma-separated

    # Operational details
    team_size = Column(String, default="")     # small/medium/large
    geography = Column(Text, default="")       # states/regions
    min_budget = Column(String, default="")    # in lakhs
    max_budget = Column(String, default="")    # in lakhs

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())