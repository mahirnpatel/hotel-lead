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

8. Expected attendance — extract the actual attendance number or range from the scraped content if mentioned e.g. "10,000" or "500-1,000". If not found, return null.

9. Attendee origin — classify where attendees are traveling from using EXACTLY one of these four values:
   - "local" — most attendees are from the same city, no significant travel required
   - "regional" — attendees travel from within the same state or neighboring states, mostly drive-in
   - "national" — attendees fly in from across the country, multiple states represented
   - "international" — attendees travel from multiple countries
   Use signals from the scraped content such as: event marketing language ("join us from across the country"), speaker home cities, sponsor headquarters locations, past attendance geographic data, or the event's industry scope.

10. Attendee origin reasoning — one sentence explaining why you assigned that origin classification. Reference specific signals from the content e.g. "Event website states attendees from 40+ countries" or "All sponsors and speakers are Dallas-based, no travel language found."

11. Is recurring — return true if the event is annual or recurring, false if it is a one-time event, null if unknown. Look for language like "annual", "Xth edition", "join us again", or year references in the event name.

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
    "confidence": "",
    "expected_attendance": null,
    "attendee_origin": "",
    "attendee_origin_reasoning": "",
    "is_recurring": null
}}

Return only valid JSON, no extra text.
"""