import os
import json
import asyncio
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled, ModelSettings, InputGuardrail, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, RunContextWrapper
import logfire


logfire.configure()
logfire.instrument_openai_agents()
load_dotenv()

BASE_URL = os.getenv("BASE_URL") 
API_KEY = os.getenv("API_KEY") 
MODEL_NAME = os.getenv("MODEL_NAME") 

if not BASE_URL or not API_KEY or not MODEL_NAME:
    raise ValueError(
        "Please set BASE_URL, API_KEY, and MODEL_NAME."
    )


client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)
set_tracing_disabled(disabled=True)
client = AsyncOpenAI(base_url=BASE_URL, api_key=API_KEY)

# --- Models for structured outputs ---

class TrendingNews(BaseModel):
    topic: str
    headlines: List[str]
    frequency: int
    summary: str

class FactCheckResult(BaseModel):
    claim: str
    verdict: str
    sources: List[str]
    summary: str

class NewsSummary(BaseModel):
    topic: str
    bullet_points: List[str]
    full_summary: str


@dataclass
class NewsUserContext:
    user_id: str
    preferred_categories: Optional[List[str]] = None
    last_query_time: Optional[datetime] = None

    def __post_init__(self):
        if self.preferred_categories is None:
            self.preferred_categories = []
        if self.last_query_time is None:
            self.last_query_time = datetime.now()

# --- Dummy Tools ---

@function_tool
def get_trending_news(topic: Optional[str] = None, category: Optional[str] = None) -> str:
    # Simulated trending news
    dummy_data = {
        "tech": [
            {"topic": "AI advancements", "headlines": [
                "OpenAI releases GPT-5",
                "Apple unveils new AI chip",
                "Microsoft invests in robotics startup"],
             "frequency": 12,
             
            },
            {"topic": "Quantum Computing breakthrough", "headlines": [
                "IBM achieves stable qubits at room temperature",
                "Google announces quantum network tests"],
             "frequency": 5, 
            }
        ],
        "finance": [
            {"topic": "Stock Market Rally", "headlines": [
                "Nasdaq hits all-time high",
                "Analysts predict continued growth"],
             "frequency": 9,
             
            },
            {"topic": "Interest Rate Cuts", "headlines": [
                "Fed signals possible rate cuts",
                "European banks lower rates to boost growth"],
             "frequency": 6,
             
             }
        ]
    }
    # Flat list if topic not specified, filter otherwise
    all_data = [item for cat in dummy_data.values() for item in cat]
    if category in dummy_data:
        relevant = dummy_data[category]
    elif topic:
        relevant = [item for item in all_data if topic.lower() in item["topic"].lower()]
    else:
        relevant = all_data
    return json.dumps(relevant[:3])

@function_tool
def fact_check_claim(claim: str) -> str:
    # Dummy fact-checking, with plausible sources
    known = {
        "Apple acquire OpenAI": {
            "verdict": "False",
            "sources": [
                "TechCrunch, 2025-08-01: No public acquisition",
                "Reuters, 2025-07-30: Apple and OpenAI in partnership talks"
            ],
            "summary": "There is no verified report of Apple acquiring OpenAI; sources suggest only collaborations."
        },
        "SpaceX launches Mars colony": {
            "verdict": "Unsubstantiated",
            "sources": [
                "NASA Blog, 2025-07-20: SpaceX plans Mars mission for 2026",
                "CNN, 2025-08-02: No reports of actual Mars colony established"
            ],
            "summary": "No credible news confirms a Mars colony launch by SpaceX; plans are underway, but not realized."
        }
    }
    for k in known:
        if k.lower() in claim.lower():
            data = known[k]
            return json.dumps({
                "claim": claim,
                **data
            })
    # Unknown claim: default simulate verification
    return json.dumps({
        "claim": claim,
        "verdict": "Unverified",
        "sources": [],
        "summary": "No sufficient evidence to verify this claim at this time."
    })
    
@function_tool
def summarize_news(article_text: str, topic: Optional[str] = None) -> str:
    # Dummy summarization: returns 3-5 generic summary bullets for any article
    bullets = [
        "Key events outlined and context provided.",
        "Expert opinions and implications discussed.",
        "Outcome and next steps suggested.",
        "Stakeholders and affected parties identified.",
        "Possible future developments mentioned."
    ]
    topic_title = topic or "General News"
    return json.dumps({
        "topic": topic_title,
        "bullet_points": bullets[:5],
        "full_summary": " ".join(bullets)
    })

# --- Specialists (Agents) ---

trending_news_agent = Agent[NewsUserContext](
    name="Trending News Agent",
    handoff_description="Find and summarize trending news topics by category.",
    instructions="""
You are a NEWS TRENDING SPECIALIST. Your responsibility is to:
- Retrieve and present current trending news topics and headlines using the get_trending_news tool.
- Only answer queries that relate to top stories, popular headlines, breaking news, or trending topics.
- Group similar stories by topic, rank them by frequency.
- NEVER answer verification or summarization requests. If you receive such a query, do not respond; escalate to the correct agent.
- Format all outputs according to the TrendingNews Pydantic model.
""",
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[get_trending_news],
    output_type=TrendingNews
)


fact_checker_agent = Agent[NewsUserContext](
    name="Fact Checker Agent",
    handoff_description="Verify the accuracy of claims using facts and citations.",
    instructions="""
You are a NEWS FACT CHECKER. Your responsibility is to:
- Use the fact_check_claim tool to assess the truthfulness of claims or rumors related to current events, news, and public figures.
- Only respond to direct requests for verification or fact-checking (e.g., those starting with 'Did', 'Is it true', 'Verify', 'Fact check').
- Never answer general news or summarization requests; ignore such prompts.
- Always cite the sources you use in your verdict.
- Format every output strictly as a FactCheckResult Pydantic model.
""",
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[fact_check_claim],
    output_type=FactCheckResult
)


news_summarizer_agent = Agent[NewsUserContext](
    name="News Summarizer Agent",
    handoff_description="Summarize articles or topics into simple points.",
    instructions="""
You are a NEWS SUMMARIZER AGENT. Your responsibility is to:
- Use the summarize_news tool to condense long-form news articles, pasted news text, or broad topics into 3–5 informative bullet points and a brief written summary.
- Only answer summarization requests (explicitly asking to 'summarize' or pasting in a chunk of news text).
- Do not respond to fact-check or trending requests. Escalate those queries to the proper specialist.
- Always validate your output against the NewsSummary Pydantic model before responding.
""",
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[summarize_news],
    output_type=NewsSummary
)


# --- Conversation Agent (Controller) ---

conversation_agent = Agent[NewsUserContext](
    name="NewsSense Controller",
    instructions="""
    You are NewsSense: route user queries to the correct agent based on whether they asked for trending news, claim verification, or news summaries.
    Classify: 
     - Trends: If they ask 'what's trending' or 'top stories'
     - Verify: If they provide a claim ('Did ... happen?' or 'Is it true ...')
     - Summarize: Pastes article text, or says 'summarize ...'
    Log all decisions with Logfire.
    Always validate input/output with pydantic models.
    """,
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
    tools=[],
    handoffs=[trending_news_agent, fact_checker_agent, news_summarizer_agent]
)

# --- Main Function ---

async def main():
    user_context = NewsUserContext(
        user_id="user456",
        preferred_categories=["tech", "finance"]
    )

    print("Welcome to NewsSense! (Type 'exit' or 'quit' to leave)\n")
    while True:
        query = input("\nYou: ").strip()
        if query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        try:
            result = await Runner.run(conversation_agent, query, context=user_context)
            print("\nNewsSense: ")

            if hasattr(result.final_output, "topic") and hasattr(result.final_output, "headlines"):
                trending = result.final_output
                print(f"🌏 TRENDING TOPIC: {trending.topic.upper()}")
                for i, h in enumerate(trending.headlines, 1):
                    print(f"{i}. {h}")
                print(f"Frequency: {trending.frequency}")
                print(f"Summary: {trending.summary}\n")

            elif hasattr(result.final_output, "claim"):
                fact = result.final_output
                print(f"❓ CLAIM: {fact.claim}")
                print(f"Verdict: {fact.verdict}")
                print("Sources:")
                for s in fact.sources:
                    print(f"- {s}")
                print(f"Summary: {fact.summary}\n")

            elif hasattr(result.final_output, "bullet_points"):
                summary = result.final_output
                print(f"✍️ SUMMARY FOR TOPIC: {summary.topic}")
                for b in summary.bullet_points:
                    print(f"- {b}")
                print(f"Summary: {summary.full_summary}\n")

            else:
                print(result.final_output)
        except InputGuardrailTripwireTriggered as e:
            print("\n⚠️ GUARDRAIL TRIGGERED ⚠️")


if __name__ == "__main__":
    asyncio.run(main())
