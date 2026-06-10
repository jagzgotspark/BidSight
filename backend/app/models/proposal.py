from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from app.database import Base


class Proposal(Base):
    __tablename__ = "proposals"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    tender_id = Column(String, nullable=False)

    # Input
    company_profile_text = Column(Text, default="")  # extracted from PDF or typed
    past_projects = Column(Text, default="")          # user-provided past work
    additional_notes = Column(Text, default="")

    # Generated output
    executive_summary = Column(Text, default="")
    capability_statement = Column(Text, default="")
    methodology = Column(Text, default="")
    team_structure = Column(Text, default="")
    timeline = Column(Text, default="")
    why_us = Column(Text, default="")

    # Meta
    status = Column(String, default="draft")  # draft, generated, exported
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())