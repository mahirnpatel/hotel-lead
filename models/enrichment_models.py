from pydantic import BaseModel, Field
from typing import Optional, List

class Stakeholder(BaseModel):
    name: str = Field(..., description="Full name of the stakeholder")
    role: str = Field(..., description="Their role or title at the event e.g. CFO The Home Depot, Keynote Speaker")
    type: str = Field(..., description="Their participation type e.g. Keynote Speaker, Organizer, Guest Speaker, Panelist")

class ProfessionalProfile(BaseModel):
    industries: List[str] = Field(..., description="Industries represented by attendees e.g. Logistics, Supply Chain, Manufacturing")
    job_titles: List[str] = Field(..., description="Job titles likely attending the event e.g. VP of Supply Chain, Operations Manager")

class TargetContacts(BaseModel):
    job_titles: List[str] = Field(..., description="Job titles to search in Apollo — people who manage travel and accommodations for their teams e.g. Corporate Travel Manager, Executive Assistant")
    reasoning: str = Field(..., description="Why these titles are the right outreach targets for this specific event")

class EventEnrichment(BaseModel):
    event_id: str = Field(..., description="PredictHQ event ID, links back to EventSummary in the research report")
    event_name: str = Field(..., description="Full name of the event as found on the event website")
    event_website: Optional[str] = Field(default=None, description="Official event website URL extracted from scraped content")
    attending_organizations: List[str] = Field(default_factory=list, description="Companies attending as exhibitors, sponsors, or partners — excludes event infrastructure vendors")
    stakeholders: List[Stakeholder] = Field(default_factory=list, description="Key figures at the event — speakers, organizers, and notable attendees")
    professional_profile: ProfessionalProfile = Field(..., description="Profile of the typical attendee — used to identify target companies in Apollo")
    target_contacts: TargetContacts = Field(..., description="Who a hotel should reach out to inside attending companies — not the attendees themselves")
    hotel_lead_reasoning: str = Field(..., description="Concrete explanation of why this event represents a hotel accommodation opportunity")
    hotel_lead_score: int = Field(..., ge=1, le=10, description="Hotel lead potential score 1-10a. 10 = major national multi-day B2B conference with high out-of-town attendance")
    confidence: str = Field(..., pattern="^(high|medium|low)$", description="Confidence in the enrichment quality based on how much data was found in scraped content")

class EnrichmentReport(BaseModel):
    city: str = Field(..., description="City that was searched, always a runtime parameter never hardcoded")
    state: str = Field(..., description="US state that was searched, always a runtime parameter never hardcoded")
    total_events: int = Field(..., description="Total number of events passed in from the research agent for enrichment")
    enriched_events: List[EventEnrichment] = Field(default_factory=list, description="Fully enriched event records ready to be consumed by Agent 2")