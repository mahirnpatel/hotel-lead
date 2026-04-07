import os
import json
from openai import OpenAI
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models.enrichment_models import EventEnrichment, EnrichmentReport
from prompts.email_prompts import EMAIL_PROMPT_TEMPLATE
from config.settings import EMAIL_AGENT_MODEL

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

HOTEL_CONTEXT = {
    "company_name": "Kriya Hotels",
    "website": "https://www.kriyahotels.com",
    "relevant_property": {
        "name": "Home2 Suites by Hilton Irving/DFW Airport North",
        "address": "4700 Plaza Dr, Irving, TX 75063",
        "url": "https://www.hilton.com/en/hotels/dalivht-home2-suites-irving-dfw-airport-north/",
        "highlights": [
            "Extended-stay suites ideal for multi-night business travelers",
            "Minutes from Irving Convention Center at Las Colinas",
            "All-suite format with full kitchens — great for week-long stays",
            "Complimentary breakfast daily",
            "Hilton Honors points eligible",
            "Free airport shuttle to DFW",
        ],
    },
    "offer": {
        "discount": "15% off standard rates for groups of 5+ rooms",
        "perk": "Complimentary room upgrade for the group organizer",
        "cancellation": "Flexible cancellation up to 7 days before check-in",
        "deadline": "May 10, 2026",
    },
}

# Mock contact — simulates Apollo Agent 2 output
# Swap this list for real ContactList later, nothing else changes
MOCK_CONTACTS = [
    {
        "name": os.getenv("RECIPIENT_NAME", "Team"),
        "company": os.getenv("RECIPIENT_COMPANY", "Your Company"),
        "email": os.getenv("RECIPIENT_EMAIL"),
        "title": "Corporate Travel Manager",
    }
]


def build_prompt(enrichment: EventEnrichment, recipient_name: str, recipient_company: str) -> str:
    highlights = "\n".join(f"  - {h}" for h in HOTEL_CONTEXT["relevant_property"]["highlights"])
    offer = HOTEL_CONTEXT["offer"]
    prop = HOTEL_CONTEXT["relevant_property"]
    return EMAIL_PROMPT_TEMPLATE.format(
        recipient_name=recipient_name,
        recipient_company=recipient_company,
        event_name=enrichment.event_name,
        event_dates="See event website",
        event_location=enrichment.event_website or "Dallas-Fort Worth, TX",
        attending_organizations=", ".join(enrichment.attending_organizations[:5]),
        hotel_lead_reasoning=enrichment.hotel_lead_reasoning,
        property_name=prop["name"],
        property_address=prop["address"],
        property_url=prop["url"],
        property_highlights=highlights,
        offer_discount=offer["discount"],
        offer_perk=offer["perk"],
        offer_cancellation=offer["cancellation"],
        offer_deadline=offer["deadline"],
    )

def generate_email(enrichment: EventEnrichment, recipient_name: str, recipient_company: str) -> dict:
    prompt = build_prompt(enrichment, recipient_name, recipient_company)
    response = client.chat.completions.create(
        model=EMAIL_AGENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        clean = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)


def send_email(subject: str, body: str, recipient_email: str) -> str:
    message = Mail(
        from_email=os.getenv("SENDER_EMAIL"),
        to_emails=recipient_email,
        subject=subject,
        html_content=body,
    )
    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)
        return "sent" if response.status_code == 202 else f"failed:{response.status_code}"
    except Exception as e:
        return f"error:{e.body}"


async def run_email_agent(enrichment_report: EnrichmentReport) -> list:
    outreach_log = []

    for enrichment in enrichment_report.enriched_events:
        for contact in MOCK_CONTACTS:
            email_data = generate_email(enrichment, contact["name"], contact["company"])
            status = send_email(email_data["subject"], email_data["body"], contact["email"])

            entry = {
                "event": enrichment.event_name,
                "recipient_name": contact["name"],
                "recipient_company": contact["company"],
                "recipient_email": contact["email"],
                "subject": email_data["subject"],
                "status": status,
            }
            outreach_log.append(entry)
            print(f"  [{status}] → {contact['name']} at {contact['company']} | {enrichment.event_name}")

    return outreach_log