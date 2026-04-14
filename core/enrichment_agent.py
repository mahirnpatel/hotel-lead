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

semaphore = asyncio.Semaphore(3)

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# ── Helper: Serper web search ──────────────────────────────────────────────────
async def search_event_urls(event_name: str, city: str) -> tuple[list[str], list[str]]:
    print(f"  [Serper] Searching URLs for: {event_name} in {city}")
    queries = [
        f"{event_name} {city} 2026 official site",
        f"{event_name} {city} 2026 sponsors exhibitors partners",
        f"{event_name} {city} 2026 speakers keynote agenda"
    ]
    urls = []
    snippets = []
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
                # collect snippets as fallback content
                snippet = r.get("snippet", "")
                title = r.get("title", "")
                if snippet:
                    snippets.append(f"**{title}**\n{snippet}")

    print(f"  [Serper] Found {len(urls)} URLs: {urls}")
    return urls, snippets


# ── Helper: fallback direct scrape ────────────────────────────────────────────
async def direct_scrape(url: str) -> str:
    loop = asyncio.get_event_loop()
    def _get():
        try:
            r = requests.get(url, headers=BROWSER_HEADERS, timeout=10)
            if r.status_code == 200:
                # strip HTML tags roughly
                import re
                text = re.sub(r'<[^>]+>', ' ', r.text)
                text = re.sub(r'\s+', ' ', text).strip()
                return text[:8000]
            return ""
        except Exception:
            return ""
    return await loop.run_in_executor(None, _get)


# ── Helper: Firecrawl scraper with fallback ────────────────────────────────────
async def scrape_urls(urls: list[str], snippets: list[str]) -> str:
    print(f"  [Firecrawl] Scraping {len(urls)} pages...")
    scraped = []
    loop = asyncio.get_event_loop()
    total_chars = 0

    for url in urls:
        def _scrape(u=url):
            return requests.post(
                "https://api.firecrawl.dev/v1/scrape",
                headers={
                    "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": u,
                    "formats": ["markdown"],
                    "mobile": True,
                    "skipTlsVerification": True,
                }
            )
        try:
            response = await loop.run_in_executor(None, _scrape)
            data = response.json()
            content = data.get("data", {}).get("markdown", "")

            if len(content) < 200:
                # Firecrawl returned empty or near-empty — try direct scrape
                print(f"  [Firecrawl] Empty for {url} — trying direct scrape")
                content = await direct_scrape(url)
                if len(content) > 200:
                    print(f"  [Direct] Got {len(content)} chars from {url}")
                else:
                    print(f"  [Direct] Also empty for {url}")

            if content:
                scraped.append(content[:8000])
                total_chars += len(content)
            print(f"  [Firecrawl] {url} — {len(content)} chars")

        except Exception as e:
            print(f"  [Firecrawl] Failed: {url} — {str(e)}")

    # If all scraping failed, fall back to Serper snippets
    if total_chars < 500 and snippets:
        print(f"  [Fallback] Using Serper snippets — {len(snippets)} snippets")
        scraped.append("SEARCH RESULT SNIPPETS:\n" + "\n\n".join(snippets))

    return "\n\n---\n\n".join(scraped)


# ── Helper: LLM enrichment for a single event ─────────────────────────────────
async def enrich_single_event(event: EventSummary, client: AsyncOpenAI, semaphore: asyncio.Semaphore) -> EventEnrichment:
    async with semaphore:
        print(f"\n[Enrichment] Starting: {event.title}")

        urls, snippets = await search_event_urls(event.title, event.city)
        combined_content = await scrape_urls(urls, snippets)

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
            event_start_date=event.start,
            event_end_date=event.end,
            duration_days=event.duration_days,
            venue_name=event.venue_name,
            venue_address=event.venue_address,
            expected_attendance=str(raw["expected_attendance"]) if raw.get("expected_attendance") is not None else None,
            attendee_origin=raw.get("attendee_origin", "national"),
            attendee_origin_reasoning=raw.get("attendee_origin_reasoning", ""),
            is_recurring=raw.get("is_recurring"),
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