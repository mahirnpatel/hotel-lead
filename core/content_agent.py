import json
from openai import OpenAI
from models.enrichment_models import EventEnrichment
from prompts.content_prompts import BLOG_PROMPT_TEMPLATE
from config.settings import CONTENT_AGENT_MODEL, OPENAI_API_KEY
from core.email_agent import HOTEL_CONTEXT


class BlogPost:
    def __init__(self, seo_title: str, meta_description: str, slug: str, body_markdown: str):
        self.seo_title = seo_title
        self.meta_description = meta_description
        self.slug = slug
        self.body_markdown = body_markdown


def generate_blog_post(event: EventEnrichment, city: str, state: str) -> BlogPost:
    hotel_name   = HOTEL_CONTEXT["relevant_property"]["name"]
    hotel_url    = HOTEL_CONTEXT["relevant_property"]["url"]
    company_name = HOTEL_CONTEXT["company_name"]
    company_url  = HOTEL_CONTEXT["website"]
    highlights   = "\n".join(f"- {h}" for h in HOTEL_CONTEXT["relevant_property"]["highlights"])

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
        hotel_url=hotel_url,
        company_name=company_name,
        company_url=company_url,
        hotel_highlights=highlights,
    )

    response = client.chat.completions.create(
        model=CONTENT_AGENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=4000,
    )

    raw = json.loads(response.choices[0].message.content)
    print(f"[Content Agent] Blog generated — title: {raw.get('seo_title')}")

    return BlogPost(
        seo_title=raw.get("seo_title", ""),
        meta_description=raw.get("meta_description", ""),
        slug=raw.get("slug", ""),
        body_markdown=raw.get("body_markdown", ""),
    )


def refine_blog_post(original_blog: BlogPost, instruction: str) -> BlogPost:
    print(f"\n[Content Agent] Refining blog — instruction: {instruction}")

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""You are an expert hotel marketing copywriter. You have written a blog post and the user wants to refine it.

Original SEO Title:
{original_blog.seo_title}

Original Meta Description:
{original_blog.meta_description}

Original Blog Body (Markdown):
{original_blog.body_markdown}

User Instruction:
{instruction}

Rewrite the blog post following the instruction. Keep the same structure and markdown formatting.
Return ONLY a JSON object with exactly four keys: "seo_title", "meta_description", "slug", "body_markdown".
Do not include any explanation or markdown code fences."""

    response = client.chat.completions.create(
        model=CONTENT_AGENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=4000,
    )

    raw = json.loads(response.choices[0].message.content)
    print(f"[Content Agent] Blog refined — title: {raw.get('seo_title')}")

    return BlogPost(
        seo_title=raw.get("seo_title", original_blog.seo_title),
        meta_description=raw.get("meta_description", original_blog.meta_description),
        slug=raw.get("slug", original_blog.slug),
        body_markdown=raw.get("body_markdown", original_blog.body_markdown),
    )