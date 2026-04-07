from pydantic import BaseModel, Field
from typing import Optional, List

class EventSummary(BaseModel):
    id: str = Field(..., description="Unique PredictHQ event ID")
    title: str = Field(..., description="Full name of the event")
    description: Optional[str] = Field(default=None, description="Event description from PredictHQ, explains audience and purpose")
    category: str = Field(..., description="PredictHQ category e.g. conferences, expos")
    labels: List[str] = Field(default_factory=list, description="Legacy PredictHQ labels e.g. business-conference, trade-show")
    phq_labels: List[str] = Field(default_factory=list, description="AI assigned labels e.g. technology, finance, healthcare, agriculture")
    rank: int = Field(..., description="PredictHQ global rank 0-100, higher means larger event")
    local_rank: Optional[int] = Field(default=None, description="Local impact rank 0-100, how big the event is relative to the city")
    phq_attendance: Optional[int] = Field(default=None, description="Predicted total attendance number from PredictHQ")
    predicted_event_spend: Optional[int] = Field(default=None, description="Total predicted USD spend across all industries at this event")
    accommodation_spend: Optional[int] = Field(default=None, description="Predicted USD spend specifically on hotel accommodation — primary hotel revenue signal")
    start: str = Field(..., description="Event start date ISO format YYYY-MM-DD, used for outreach timing")
    end: str = Field(..., description="Event end date ISO format YYYY-MM-DD")
    duration_days: Optional[int] = Field(default=None, description="Number of days the event runs, longer = more overnight stays needed")
    city: str = Field(..., description="City where the event is taking place")
    state: str = Field(..., description="US state where the event is taking place")
    venue_name: Optional[str] = Field(default=None, description="Venue name e.g. Georgia World Congress Center, used to assess event scale")
    venue_address: Optional[str] = Field(default=None, description="Full venue address, used by Agent 2 to find nearby companies on Apollo")
    relevance_score: int = Field(..., ge=1, le=10, description="Hotel lead potential score 1-10. 10 = major national B2B conference. 1 = local free community event")
    relevance_reason: str = Field(..., description="One concrete sentence explaining the hotel opportunity, references real data like attendance and spend")
    estimated_attendees: Optional[str] = Field(default=None, description="Human readable attendance estimate e.g. 4500 or 500-1000, uses phq_attendance if available")
    target_companies: List[str] = Field(default_factory=list, description="3-5 specific company types likely sending attendees e.g. steel fabricators, SaaS startups, hedge funds")

class EventIntelligenceReport(BaseModel):
    city: str = Field(..., description="City that was searched, always runtime parameter never hardcoded")
    state: str = Field(..., description="US state that was searched, always runtime parameter never hardcoded")
    generated_at: str = Field(..., description="UTC timestamp when this report was generated, ISO format")
    total_found: int = Field(..., description="Total events returned by PredictHQ before any filtering")
    filtered_out: int = Field(..., description="Events dropped by LLM scoring below threshold of 6")
    events: List[EventSummary] = Field(default_factory=list, description="High potential events only, relevance score >= 5, sorted by score descending")