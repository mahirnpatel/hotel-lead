import os
from dotenv import load_dotenv

load_dotenv(override=True)

OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY")
PREDICTHQ_API_KEY = os.getenv("PREDICTHQ_API_KEY")
APOLLO_API_KEY    = os.getenv("APOLLO_API_KEY")
SERPER_API_KEY   = os.getenv("SERPER_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# SUPABASE_URL      = os.getenv("SUPABASE_URL")
# SUPABASE_KEY      = os.getenv("SUPABASE_KEY")

RESEARCH_AGENT_MODEL = "gpt-4.1"
ENRICHMENT_AGENT_MODEL = "gpt-4.1-mini"
SALES_AGENT_MODEL    = "gpt-4.1-mini"
EMAIL_AGENT_MODEL    = "gpt-4.1-mini"
CONTENT_AGENT_MODEL  = "gpt-4.1-mini"


MIN_RELEVANCE_SCORE  = 6
MIN_PREDICTHQ_RANK   = 30
DEFAULT_DAYS_FROM    = 40
DEFAULT_DAYS_WINDOW  = 180
DEFAULT_LIMIT        = 25

START_DATE = None  # Set at runtime by UI
END_DATE   = None  # Set at runtime by UI