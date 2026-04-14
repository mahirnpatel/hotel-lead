BLOG_PROMPT_TEMPLATE = """
You are an expert hotel marketing copywriter specializing in SEO content for event-based hotel accommodation pages.
You have been given details about an upcoming event and the hotel that wants to capture accommodation bookings from attendees.
Your job is to write a complete, publish-ready SEO blog post that targets corporate professionals searching for hotels near this event.

EVENT DETAILS:
Event Name: {event_name}
City: {city}
State: {state}
Dates: {event_start_date} to {event_end_date}
Duration: {duration_days} days
Venue: {venue_name}
Expected Attendance: {expected_attendance}
Attendee Origin: {attendee_origin}
Attending Organizations: {attending_organizations}
Professional Profile: {professional_profile}
Hotel Lead Reasoning: {hotel_lead_reasoning}

HOTEL DETAILS:
Hotel Name: {hotel_name}
Hotel URL: {hotel_url}
Company Name: {company_name}
Company Website: {company_url}
Property Highlights:
{hotel_highlights}

INSTRUCTIONS:
Write a complete, detailed SEO blog post following this exact structure. Each section must be substantive — this is a 1500-2500 word article, not a short overview.

1. SEO TITLE — Compelling title targeting "[Hotel Name] — [Event Name] [Year] Accommodations" and variations. Must include event name, city, and year.

2. META DESCRIPTION — 150-160 characters. Include event name, hotel name, and a call to action.

3. INTRODUCTION (3-4 paragraphs) — Open with the scale and significance of the event. Reference attendance numbers, the professional caliber of attendees, the dates, and why accommodation planning matters early. Build urgency without being generic. Make it feel like insider knowledge from someone who understands both the event and the hospitality market.

4. ABOUT THE EVENT (2-3 paragraphs) — Explain what the event is, who attends, which organizations send teams, and what the professional profile looks like. Reference the attending organizations and industries. This section targets people researching the event and helps with broad SEO.

5. WHO NEEDS ACCOMMODATION (2 paragraphs) — Be specific about the types of professionals who travel to this event. Reference the job titles and company types from the professional profile. Make it clear this is for business travelers — not tourists — who need reliable, comfortable accommodation close to the venue.

6. WHY STAY AT {hotel_name} (3-4 paragraphs) — Use the property highlights listed above to write specific, accurate reasons to book at this hotel. Reference the exact amenities from the highlights — do not invent anything not listed. For location, use the city and venue name to reason about proximity — if the hotel and venue are in the same metro area, write "minutes from [venue]" or "conveniently located near [venue]". Mention that {company_name} manages this property and include {company_url} as a reference. Include {hotel_url} as a direct booking link in the text.

7. AMENITIES FOR BUSINESS TRAVELERS (1-2 paragraphs + bullet list) — Pull directly from the property highlights above. List only the amenities that are explicitly mentioned in the highlights. Frame each one in terms of why it matters for someone attending this specific event. Do not add amenities that are not in the highlights.

8. LOCATION AND DISTANCE (1-2 paragraphs) — Describe the hotel's location relative to the event venue and city. Use the city, state, and venue name provided. If the hotel is near a major airport or convention center, mention it. Write confidently about proximity using language like "positioned in the heart of [city]", "minutes from [venue]", or "easy access to [venue] via [major highway or area]". Do not fabricate exact mileage — use directional and time-based language instead.

9. GROUP BOOKING ADVANTAGES (2 paragraphs) — Explain the value of booking as a group. Cover group rates, room blocks, a single point of contact, flexible attrition, and the benefit of having your team housed together. Reference the types of companies attending this event that would benefit from group blocks.

10. CALL TO ACTION (1-2 paragraphs) — Strong closing with urgency referencing the event dates and limited room availability. Direct the reader to {hotel_url} to explore the property. Mention {company_name} and link to {company_url}. Give a clear instruction to contact for group rates. Mention that rooms fill up fast for major industry events.

11. FAQ SECTION (5-6 questions) — Write natural, specific question-and-answer pairs targeting long-tail SEO keywords. Questions should reflect what a corporate travel manager or event coordinator would actually search. Include questions about group rates, proximity to venue, amenities, booking deadlines, and cancellation policies. Reference the hotel name and event name in the answers.

TONE: Professional, confident, and specific. Write like a knowledgeable hospitality insider who understands corporate travel — not a marketing robot. Every paragraph should feel written for THIS event and THIS hotel, not copy-pasted from a template.

IMPORTANT:
- Use the event name, city, hotel name, and year naturally and frequently throughout — this is SEO content
- Every section must be specific to this event and this hotel
- Pull amenities directly from the property highlights — do not invent facts
- Include {hotel_url} and {company_url} naturally in the text, especially in sections 6 and 10
- Do not fabricate exact distances or mileage — use directional and time-based language
- Aim for 1500-2500 words total
- Write in proper markdown with ## for section headers and ### for FAQ questions

Respond in this exact JSON format:
{{
    "seo_title": "",
    "meta_description": "",
    "slug": "",
    "body_markdown": ""
}}

The body_markdown field should contain the full blog post in clean markdown starting from the introduction. Do not repeat the title in the body. Use ## for section headers and ### for FAQ questions.
Return only valid JSON, no extra text.
"""