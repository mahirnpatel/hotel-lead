import requests
from datetime import datetime, timezone, timedelta
from typing import Literal, List
from agents import function_tool
from config.settings import PREDICTHQ_API_KEY, DEFAULT_DAYS_FROM, DEFAULT_DAYS_WINDOW, DEFAULT_LIMIT, MIN_PREDICTHQ_RANK
from config.settings import START_DATE, END_DATE

PredictHQCategory = Literal[
    "politics",
    "conferences", "expos", "concerts", "festivals", "sports"
]

JUNK_KEYWORDS = [
    "collectible", "collectibles", "trading card", "tcg", "pokemon",
    "hot wheels", "funko", "comic", "hobby", "streetwear",
    "gothic market", "dj retreat", "q&a", "swap meet",
    "craft & gift", "flash tattoo", "furry", "frolicon"
]


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


@function_tool
def search_events(
    city:          str,
    state:         str,
    categories:    list[PredictHQCategory] = ["conferences", "expos"],
    min_rank:      int  = 30,
    limit:         int  = 25
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
        "country":    "US",
        "active.gte": date_from,
        "active.lte": date_to,
        "category":   ",".join(categories),
        "rank.gte":   min_rank,
        "limit":      limit,
        "sort":       "rank",
        
        "predicted_event_spend_industry.accommodation.gte": 50000,
        "phq_attendance.gte": 200,
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

    # ── Basic junk keyword filter ──────────────────────────────────
    JUNK_KEYWORDS = [
        "collectible", "collectibles", "trading card", "tcg", "pokemon",
        "hot wheels", "funko", "comic", "hobby", "streetwear",
        "gothic market", "dj retreat", "q&a", "swap meet",
        "craft & gift", "flash tattoo", "furry", "frolicon"
    ]

    def is_junk(event: dict) -> bool:
        return any(kw in event["title"].lower() for kw in JUNK_KEYWORDS)

    filtered = [e for e in data.get("results", []) if not is_junk(e)]

    print(f"  Total from API:    {data.get('count', 0)}")
    print(f"  Returned:          {len(data.get('results', []))}")
    print(f"  After junk filter: {len(filtered)}")

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
        "pre_llm_dropped": len(data.get("results", [])) - len(filtered),
        "events": [
            {
                "id":              e["id"],
                "title":           e["title"],
                "description":     e.get("description", ""),
                "category":        e["category"],
                "labels":          e.get("labels", []),
                "phq_labels":      [l["label"] for l in e.get("phq_labels", [])],
                "rank":            e["rank"],
                "local_rank":      e.get("local_rank"),
                "phq_attendance":  e.get("phq_attendance"),
                "predicted_event_spend": e.get("predicted_event_spend"),
                "accommodation_spend":   e.get("predicted_event_spend_industries", {}).get("accommodation"),
                "start":           e["start"],
                "end":             e["end"],
                "duration_days":   get_duration_days(e),
                "venue_name":      get_venue(e),
                "venue_address":   get_venue_address(e),
                "city":            city,
                "state":           state,
            }
            for e in filtered
        ]
    }