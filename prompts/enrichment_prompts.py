ENRICHMENT_PROMPT_TEMPLATE = """
You are a hotel sales intelligence analyst. You have been given details about an upcoming event and scraped content from its web pages.
Your job is to analyze this event and determine its value as a hotel lead opportunity.

EVENT DETAILS:
Name: {name}
City: {city}
Date: {date}
Duration: {duration_days} days
Predicted Attendance: {predicted_attendance}
Summary: {summary}

SCRAPED WEB CONTENT:
{combined_content}

Based on the above, extract and reason about the following:
1. Attending organizations / companies — extract only companies that are sending employees as exhibitors, sponsors, or attendees. Exclude event infrastructure/service vendors such as logistics companies managing the event, AV companies, catering, venue staff, decorators, or any company whose role is purely to operate or service the event rather than attend it as a business participant.
2. Stakeholders (speakers, organizers, key figures) — return as objects with name, role, and type fields.
3. Professional profile (what industries and job titles are likely attending this event)
4. Target contacts (who inside attending companies should a hotel reach out to — these are NOT the attendees themselves, but the people who manage travel, accommodations, and event logistics for their teams)
5. Hotel lead reasoning (why would attendees need hotel accommodation?)
6. Hotel lead score (1-10, where 10 is highest opportunity)
7. Confidence level (high/medium/low — based on how much data was found)

Respond in this exact JSON format:
{{
    "event_name": "",
    "event_website": "",
    "attending_organizations": [],
    "stakeholders": [
        {{"name": "", "role": "", "type": ""}}
    ],
    "professional_profile": {{
        "industries": [],
        "job_titles": []
    }},
    "target_contacts": {{
        "job_titles": [],
        "reasoning": ""
    }},
    "hotel_lead_reasoning": "",
    "hotel_lead_score": 0,
    "confidence": ""
}}

Return only valid JSON, no extra text.
"""