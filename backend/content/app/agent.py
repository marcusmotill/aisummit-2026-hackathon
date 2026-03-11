# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
from zoneinfo import ZoneInfo

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

import os
import google.auth

_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


from google.adk.tools import AgentTool
from google.adk.plugins.global_instruction_plugin import GlobalInstructionPlugin
from .deconstructor import get_deconstructor_agent
from .copywriter import get_copywriter_agent
from .visualizer import get_visualizer_agent

from pydantic import BaseModel, Field
from typing import List, Optional
from google.adk.agents.callback_context import CallbackContext

class CampaignAsset(BaseModel):
    title: str = Field(description="Title of the asset (e.g., Twitter Thread, LinkedIn Post)")
    content: str = Field(description="The actual copy for the asset")
    visual_suggestion: str = Field(description="Suggested visual asset or image prompt")
    channel: str = Field(description="The target channel (Twitter, LinkedIn, Email, etc.)")

class CampaignReport(BaseModel):
    summary: str = Field(description="Overall campaign theme and objectives")
    assets: List[CampaignAsset] = Field(description="List of multi-channel promotional assets")

async def save_campaign_report(callback_context: CallbackContext) -> None:
    """Saves the final Campaign Report as a JSON artifact via after_agent_callback.
    """
    # Retrieve the structured output from the session state
    report_data = callback_context.state.get("campaign_report")
    if not report_data:
        return None

    # Save as artifact
    filename = "campaign_report.json"
    content_json = json.dumps(report_data, indent=2)
    part = types.Part.from_text(text=content_json)
    await callback_context.save_artifact(filename, part)
    return None

root_agent = Agent(
    name="campaign_builder_orchestrator",
    model=Gemini(
        model="gemini-3-flash-preview",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Campaign Builder Orchestrator. Your goal is to transform long-form content "
        "into a comprehensive 'Campaign-in-a-Box' by coordinating a team of expert tools. "
        "\n\nWorkflow:"
        "\n1. Call the `deconstructor_agent` tool to extract core themes, arguments, and quotes from the provided draft."
        "\n2. Use the extracted assets as input for the `copywriter_agent` and `visualizer_agent` tools."
        "\n3. Coordinate the `copywriter_agent` to generate tailored copy for Twitter, LinkedIn, and Email."
        "\n4. Coordinate the `visualizer_agent` to suggest or generate brand-aligned visuals for each asset."
        "\n5. Compile all assets into a structured 'Campaign Report'."
    ),
    tools=[
        AgentTool(get_deconstructor_agent()),
        AgentTool(get_copywriter_agent()),
        AgentTool(get_visualizer_agent()),
    ],
    output_schema=CampaignReport,
    output_key="campaign_report",
    after_agent_callback=save_campaign_report,
)

app = App(
    root_agent=root_agent,
    name="app",
    plugins=[
        GlobalInstructionPlugin(
            global_instruction="The current year is 2026. All marketing campaigns should be designed for present-day (2026) trends and audiences. Avoid outdated 2024/2025 context."
        )
    ],
)
