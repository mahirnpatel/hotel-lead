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
    # ── Identity ───────────────────────────────────────────────────
    event_id: str = Field(..., description="PredictHQ event ID, links back to EventSummary in the research report")
    event_name: str = Field(..., description="Full name of the event as found on the event website")
    event_website: Optional[str] = Field(default=None, description="Official event website URL extracted from scraped content")

    # ── Dates & Duration ───────────────────────────────────────────
    event_start_date: Optional[str] = Field(default=None, description="Event start date in YYYY-MM-DD format, passed in from PredictHQ EventSummary")
    event_end_date: Optional[str] = Field(default=None, description="Event end date in YYYY-MM-DD format, passed in from PredictHQ EventSummary")
    duration_days: Optional[int] = Field(default=None, description="Number of days the event runs, derived from start and end date")

    # ── Venue ──────────────────────────────────────────────────────
    venue_name: Optional[str] = Field(default=None, description="Name of the venue where the event is held e.g. Dallas Market Center, Kay Bailey Hutchison Convention Center")
    venue_address: Optional[str] = Field(default=None, description="Street address of the venue, scraped from event website or passed in from PredictHQ")

    # ── Attendance ─────────────────────────────────────────────────
    expected_attendance: Optional[str] = Field(default=None, description="Approximate attendance range as a string e.g. '500-1,000' or '10,000+', scraped from event website if available")
    attendee_origin: str = Field(..., description="Geographic origin of attendees — must be exactly one of: local, regional, national, international. Inferred from event website content, speaker locations, and event scope language")
    attendee_origin_reasoning: str = Field(..., description="Brief explanation of why this origin classification was assigned e.g. 'Event marketed nationally, speakers flying in from 12 states, attendees from 40+ countries'")
    is_recurring: Optional[bool] = Field(default=None, description="Whether this is an annual or recurring event, inferred from event website language")

    # ── Organizations & People ─────────────────────────────────────
    attending_organizations: List[str] = Field(default_factory=list, description="Companies attending as exhibitors, sponsors, or partners — excludes event infrastructure vendors")
    stakeholders: List[Stakeholder] = Field(default_factory=list, description="Key figures at the event — speakers, organizers, and notable attendees")
    professional_profile: ProfessionalProfile = Field(..., description="Profile of the typical attendee — used to identify target companies in Apollo")
    target_contacts: TargetContacts = Field(..., description="Who a hotel should reach out to inside attending companies — not the attendees themselves")

    # ── Hotel Lead Assessment ──────────────────────────────────────
    hotel_lead_reasoning: str = Field(..., description="Concrete explanation of why this event represents a hotel accommodation opportunity")
    hotel_lead_score: int = Field(..., ge=1, le=10, description="Hotel lead potential score 1-10. 10 = major national multi-day B2B conference with high out-of-town attendance")
    confidence: str = Field(..., pattern="^(high|medium|low)$", description="Confidence in the enrichment quality based on how much data was found in scraped content")


class EnrichmentReport(BaseModel):
    city: str = Field(..., description="City that was searched, always a runtime parameter never hardcoded")
    state: str = Field(..., description="US state that was searched, always a runtime parameter never hardcoded")
    total_events: int = Field(..., description="Total number of events passed in from the research agent for enrichment")
    enriched_events: List[EventEnrichment] = Field(default_factory=list, description="Fully enriched event records ready to be consumed by Agent 2")