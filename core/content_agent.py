import json
from openai import OpenAI
from models.enrichment_models import EventEnrichment
from prompts.content_prompts import BLOG_PROMPT_TEMPLATE
from config.settings import CONTENT_AGENT_MODEL, OPENAI_API_KEY


class BlogPost:
    def __init__(self, seo_title: str, meta_description: str, slug: str, body_markdown: str):
        self.seo_title = seo_title
        self.meta_description = meta_description
        self.slug = slug
        self.body_markdown = body_markdown


def generate_blog_post(event: EventEnrichment, hotel_name: str, city: str, state: str) -> BlogPost:
    print(f"\n[Content Agent] Generating blog for: {event.event_name} — {hotel_name}")

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = BLOG_PROMPT_TEMPLATE.format(
        event_name=event.event_name,
        city=city,
        state=state,
        event_start_date=event.event_start_date or "TBD",
        event_end_date=event.event_end_date or "TBD",
        duration_days=event.duration_days or "TBD",
        venue_name=event.venue_name or "TBD",
        expected_attendance=event.expected_attendance or "TBD",
        attendee_origin=event.attendee_origin or "national",
        attending_organizations=", ".join(event.attending_organizations[:15]) if event.attending_organizations else "Various organizations",
        professional_profile=f"Industries: {', '.join(event.professional_profile.industries)}. Job titles: {', '.join(event.professional_profile.job_titles)}",
        hotel_lead_reasoning=event.hotel_lead_reasoning,
        hotel_name=hotel_name,
    )

    response = client.chat.completions.create(
        model=CONTENT_AGENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )

    raw = json.loads(response.choices[0].message.content)
    print(f"[Content Agent] Blog generated — title: {raw.get('seo_title')}")

    return BlogPost(
        seo_title=raw.get("seo_title", ""),
        meta_description=raw.get("meta_description", ""),
        slug=raw.get("slug", ""),
        body_markdown=raw.get("body_markdown", ""),
    )