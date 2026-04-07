import asyncio
import json
import requests
from openai import AsyncOpenAI
from models.event_models import EventIntelligenceReport, EventSummary
from models.enrichment_models import EventEnrichment, EnrichmentReport, Stakeholder, ProfessionalProfile, TargetContacts
from prompts.enrichment_prompts import ENRICHMENT_PROMPT_TEMPLATE
from config.settings import (
    ENRICHMENT_AGENT_MODEL,
    SERPER_API_KEY,
    FIRECRAWL_API_KEY,
    OPENAI_API_KEY
)
# add this at the top of run_enrichment_agent
semaphore = asyncio.Semaphore(3)
# ── Helper: Serper web search ─────────────────────────────────────────────────

async def search_event_urls(event_name: str, city: str) -> list[str]:
    print(f"  [Serper] Searching URLs for: {event_name} in {city}")
    queries = [
        f"{event_name} {city} 2026 official site",
        f"{event_name} {city} 2026 sponsors exhibitors partners",
        f"{event_name} {city} 2026 speakers keynote agenda"
    ]
    urls = []
    seen = set()

    loop = asyncio.get_event_loop()

    for query in queries:
        def _search(q=query):
            return requests.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"},
                json={"q": q, "num": 2}
            )
        response = await loop.run_in_executor(None, _search)
        results = response.json().get("organic", [])
        for r in results[:2]:
            if r["link"] not in seen:
                seen.add(r["link"])
                urls.append(r["link"])

    print(f"  [Serper] Found {len(urls)} URLs: {urls}")
    return urls


# ── Helper: Firecrawl scraper ─────────────────────────────────────────────────

async def scrape_urls(urls: list[str]) -> list[str]:
    print(f"  [Firecrawl] Scraping {len(urls)} pages...")
    scraped = []
    loop = asyncio.get_event_loop()

    for url in urls:
        def _scrape(u=url):
            return requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={
                    "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={"url": u, "formats": ["markdown"]}
            )
        try:
            response = await loop.run_in_executor(None, _scrape)
            data = response.json()
            content = data.get("data", {}).get("markdown", "")
            scraped.append(content[:8000])
            print(f"  [Firecrawl] Scraped {url} — {len(content)} chars")
        except Exception as e:
            scraped.append(f"Failed to scrape {url}: {str(e)}")
            print(f"  [Firecrawl] Failed: {url} — {str(e)}")

    return scraped


# ── Helper: LLM enrichment for a single event ─────────────────────────────────

async def enrich_single_event(event: EventSummary, client: AsyncOpenAI, semaphore: asyncio.Semaphore) -> EventEnrichment:
    async with semaphore:
        print(f"\n[Enrichment] Starting: {event.title}")

        urls = await search_event_urls(event.title, event.city)
        scraped_pages = await scrape_urls(urls)
        combined_content = "\n\n---\n\n".join(scraped_pages)

        prompt = ENRICHMENT_PROMPT_TEMPLATE.format(
            name=event.title,
            city=event.city,
            date=event.start,
            duration_days=event.duration_days or 1,
            predicted_attendance=event.phq_attendance or "Unknown",
            summary=event.relevance_reason,
            combined_content=combined_content
        )

        print(f"  [LLM] Sending enrichment prompt for: {event.title}")
        response = await client.chat.completions.create(
            model=ENRICHMENT_AGENT_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        raw = json.loads(response.choices[0].message.content)
        print(f"  [LLM] Enrichment complete for: {event.title} — score: {raw.get('hotel_lead_score')}")

        stakeholders = [
            Stakeholder(**s) if isinstance(s, dict) else Stakeholder(name=s, role="", type="")
            for s in raw.get("stakeholders", [])
        ]

        return EventEnrichment(
            event_id=event.id,
            event_name=raw.get("event_name", event.title),
            event_website=raw.get("event_website"),
            attending_organizations=raw.get("attending_organizations", []),
            stakeholders=stakeholders,
            professional_profile=ProfessionalProfile(**raw["professional_profile"]),
            target_contacts=TargetContacts(**raw["target_contacts"]),
            hotel_lead_reasoning=raw.get("hotel_lead_reasoning", ""),
            hotel_lead_score=raw.get("hotel_lead_score", 1),
            confidence=raw.get("confidence", "low")
        )


async def run_enrichment_agent(report: EventIntelligenceReport) -> EnrichmentReport:
    print(f"\n{'='*60}")
    print(f"[Enrichment Agent] Starting — {len(report.events)} events to enrich")
    print(f"{'='*60}")

    client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    semaphore = asyncio.Semaphore(3)

    tasks = [enrich_single_event(event, client, semaphore) for event in report.events]
    enriched_events = await asyncio.gather(*tasks)

    print(f"\n[Enrichment Agent] Done — {len(enriched_events)} events enriched")

    return EnrichmentReport(
        city=report.city,
        state=report.state,
        total_events=len(report.events),
        enriched_events=list(enriched_events)
    )