import requests
from datetime import datetime, timezone, timedelta
from typing import Literal
from agents import function_tool
from config.settings import PREDICTHQ_API_KEY, DEFAULT_DAYS_FROM, DEFAULT_DAYS_WINDOW, DEFAULT_LIMIT, MIN_PREDICTHQ_RANK
from config.settings import START_DATE, END_DATE

PredictHQCategory = Literal[
    "politics",
    "conferences", "expos", "concerts", "festivals", "sports"
]

JUNK_KEYWORDS = [
    # consumer/hobby events
    "collectible", "collectibles", "trading card", "tcg", "pokemon",
    "hot wheels", "funko", "comic", "hobby", "streetwear",
    "gothic market", "dj retreat", "q&a", "swap meet",
    "craft & gift", "flash tattoo", "furry", "frolicon",
    # auto/vehicle consumer events
    "auto show", "motor show", "car show", "bike tour", "motorcycle week",
    "bike week", "air show", "airshow", "horse show", "rodeo",
    # art/craft/fair events
    "art fair", "art expo", "craft fair", "arts & crafts", "arts and crafts",
    "county fair", "state fair",
    # fan/pop culture events
    "fan expo", "fan fusion", "powwow", "pow wow", "fleet week",
]

B2B_LABELS = {
    "science-and-technology",
    "medical",
    "management-and-consulting",
    "legal-and-property-services",
    "financial-services",
    "construction-and-infrastructure",
    "logistics-and-transportation",
    "manufacturing-and-petroleum-products",
    "mining-drilling-and-metalwork",
    "hospitality-and-travel",
    "automotive",
    "textile",
    "agriculture-forestry-and-fisheries",
    "consumer-goods",
    "design-and-furnishing",
    "sports-and-gaming",
}

EXCLUDE_LABELS = {
    "lifestyle",
    "art-and-cultural",
    "literature-film-and-theater",
    "festivals-and-outdoor-activities",
    "music-and-dance",
    "food-and-beverage",
    "beauty-and-fashion",
    "religion-and-spirituality",
    "education-and-careers",
}


def get_place_id(city: str, state: str) -> tuple[str, str]:
    city_clean  = city.lower().replace(" city", "").strip()
    state_clean = state.lower().strip()

    city_response = requests.get(
        "https://api.predicthq.com/v1/places/",
        headers={"Authorization": f"Bearer {PREDICTHQ_API_KEY}", "Accept": "application/json"},
        params={"q": city_clean, "country": "US", "limit": 10}
    )
    city_place_id = None
    for place in city_response.json().get("results", []):
        if (
            place.get("type") == "locality"
            and place.get("name", "").lower() == city_clean
            and place.get("region", "").lower() == state_clean
        ):
            city_place_id = place["id"]
            break

    state_response = requests.get(
        "https://api.predicthq.com/v1/places/",
        headers={"Authorization": f"Bearer {PREDICTHQ_API_KEY}", "Accept": "application/json"},
        params={"q": state_clean, "country": "US", "limit": 10}
    )
    state_place_id = None
    for place in state_response.json().get("results", []):
        if (
            place.get("type") == "region"
            and place.get("name", "").lower() == state_clean
        ):
            state_place_id = place["id"]
            break

    print(f"  city_place_id:  {city_place_id}")
    print(f"  state_place_id: {state_place_id}")
    return city_place_id, state_place_id


def _is_junk(event: dict) -> bool:
    return any(kw in event["title"].lower() for kw in JUNK_KEYWORDS)


def _is_b2b(event: dict) -> bool:
    labels = {l["label"] for l in event.get("phq_labels", [])}
    b2b_count     = len(labels & B2B_LABELS)
    exclude_count = len(labels & EXCLUDE_LABELS)
    if b2b_count == 0:
        return False
    return b2b_count >= exclude_count


@function_tool
def search_events(
    city:       str,
    state:      str,
    categories: list[PredictHQCategory] = ["conferences", "expos"],
    min_rank:   int = 20,
    limit:      int = 50
) -> dict:
    """
    Search for upcoming events in a US city using PredictHQ.
    Returns ranked business-relevant events like conferences and expos.
    City and state are always passed as runtime parameters, never hardcoded.
    """

    date_from = START_DATE or (datetime.now(timezone.utc) + timedelta(days=DEFAULT_DAYS_FROM)).strftime("%Y-%m-%d")
    date_to   = END_DATE   or (datetime.now(timezone.utc) + timedelta(days=DEFAULT_DAYS_FROM + DEFAULT_DAYS_WINDOW)).strftime("%Y-%m-%d")

    city_place_id, state_place_id = get_place_id(city, state)

    params = {
        "country":         "US",
        "active.gte":      date_from,
        "active.lte":      date_to,
        "category":        ",".join(categories),
        "rank.gte":        min_rank,
        "limit":           limit,
        "sort":            "rank",
        "phq_attendance.gte": 1000,
    }

    if city_place_id:
        params["place.scope"] = city_place_id
    elif state_place_id:
        params["place.scope"] = state_place_id
    else:
        params["q"] = f"{city} {state}"

    response = requests.get(
        "https://api.predicthq.com/v1/events/",
        headers={"Authorization": f"Bearer {PREDICTHQ_API_KEY}", "Accept": "application/json"},
        params=params,
        timeout=15
    )
    data = response.json()
    raw_results = data.get("results", [])

    # Step 1 — junk keyword filter
    after_keyword = [e for e in raw_results if not _is_junk(e)]

    # Step 2 — B2B label scoring filter
    after_label = [e for e in after_keyword if _is_b2b(e)]

    print(f"  Total from API:       {data.get('count', 0)}")
    print(f"  Returned:             {len(raw_results)}")
    print(f"  After keyword filter: {len(after_keyword)}")
    print(f"  After label filter:   {len(after_label)}")

    def get_venue(event: dict) -> str:
        for entity in event.get("entities", []):
            if entity.get("type") == "venue":
                return entity.get("name", "")
        return ""

    def get_venue_address(event: dict) -> str:
        return event.get("geo", {}).get("address", {}).get("formatted_address", "")

    def get_duration_days(event: dict) -> int:
        duration_secs = event.get("duration", 0)
        if duration_secs:
            return max(1, round(duration_secs / 86400))
        try:
            start = datetime.fromisoformat(event["start"].replace("Z", "+00:00"))
            end   = datetime.fromisoformat(event["end"].replace("Z", "+00:00"))
            return max(1, (end - start).days)
        except Exception:
            return 1

    return {
        "total_found":     data.get("count", 0),
        "pre_llm_dropped": len(raw_results) - len(after_label),
        "events": [
            {
                "id":                    e["id"],
                "title":                 e["title"],
                "description":           e.get("description", ""),
                "category":              e["category"],
                "labels":                e.get("labels", []),
                "phq_labels":            [l["label"] for l in e.get("phq_labels", [])],
                "rank":                  e["rank"],
                "local_rank":            e.get("local_rank"),
                "phq_attendance":        e.get("phq_attendance"),
                "predicted_event_spend": e.get("predicted_event_spend"),
                "accommodation_spend":   e.get("predicted_event_spend_industries", {}).get("accommodation"),
                "start":                 e["start"],
                "end":                   e["end"],
                "duration_days":         get_duration_days(e),
                "venue_name":            get_venue(e),
                "venue_address":         get_venue_address(e),
                "city":                  city,
                "state":                 state,
            }
            for e in after_label
        ]
    }