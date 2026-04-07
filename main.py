import asyncio
from core.research_agent import run_research_agent
from core.enrichment_agent import run_enrichment_agent
from core.email_agent import run_email_agent

async def main():
    cities = [
        ("Dallas", "Texas"),
    ]

    for city, state in cities:
        print(f"\n{'='*60}")
        print(f"  Researching: {city}, {state}")
        print(f"{'='*60}")

        # Agent 1: Research
        report = await run_research_agent(city, state)
        print(f"\n  Total from API:  {report.total_found}")
        print(f"  Agent kept:      {len(report.events)}")
        print(f"  Filtered out:    {report.filtered_out}\n")

        for e in sorted(report.events, key=lambda x: x.relevance_score, reverse=True):
            print(f"  [{e.relevance_score}/10] [{e.rank}] {e.title}")
            print(f"           {e.start} → {e.end}")
            print(f"           {e.relevance_reason}")
            print()

        # Agent 1.5: Enrichment
        enrichment_report = await run_enrichment_agent(report)
        print(f"\n{'='*60}")
        print(f"  Enrichment Complete: {enrichment_report.total_events} events processed")
        print(f"{'='*60}\n")

        for e in enrichment_report.enriched_events:
            print(f"  [{e.hotel_lead_score}/10] [{e.confidence}] {e.event_name}")
            print(f"           Website:  {e.event_website}")
            print(f"           Orgs:     {len(e.attending_organizations)} attending organizations")
            print(f"           Targets:  {', '.join(e.target_contacts.job_titles[:3])}")
            print(f"           Reason:   {e.hotel_lead_reasoning[:120]}...")
            print()

        # Agent 3: Email
        print(f"\n{'='*60}")
        print(f"  Running Email Agent")
        print(f"{'='*60}\n")

        outreach_log = await run_email_agent(enrichment_report)

        print(f"\n  Emails sent: {len(outreach_log)}")
        for entry in outreach_log:
            print(f"  [{entry['status']}] {entry['event']} → {entry['recipient_email']}")

if __name__ == "__main__":
    asyncio.run(main())