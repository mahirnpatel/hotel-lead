from agents import Agent, Runner, trace
from models.event_models import EventIntelligenceReport
from tools.predicthq_tool import search_events
from prompts.research_prompts import RESEARCH_AGENT_INSTRUCTIONS_V3
from config.settings import RESEARCH_AGENT_MODEL


research_agent = Agent(
    name="Research Agent",
    model=RESEARCH_AGENT_MODEL,
    instructions=RESEARCH_AGENT_INSTRUCTIONS_V3,
    tools=[search_events],
    output_type=EventIntelligenceReport
)


async def run_research_agent(city: str, state: str) -> EventIntelligenceReport:
    with trace("Research Agent — Event Discovery"):
        result = await Runner.run(
            research_agent,
            input=f"Find upcoming business events in {city}, {state}"
        )
        return result.final_output