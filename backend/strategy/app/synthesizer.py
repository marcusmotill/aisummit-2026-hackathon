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

import json

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import Gemini
from google.genai import types
from pydantic import BaseModel, Field


class GapTopic(BaseModel):
    title: str = Field(description="The catchy title for the content topic")
    description: str = Field(description="A brief description of why this is a gap")
    priority: str = Field(description="High, Medium, or Low priority")
    estimated_impact: str = Field(description="Estimated business impact score (e.g., 1-10 or qualitative)")

class ContentGapReport(BaseModel):
    summary: str = Field(description="High-level summary of the findings")
    topics: list[GapTopic] = Field(description="List of prioritized content topics")

async def save_gap_report(callback_context: CallbackContext) -> None:
    """Saves the final Content Gap Report as a JSON artifact via after_agent_callback.
    """
    # Retrieve the structured output from the session state
    report_data = callback_context.state.get("gap_report")
    if not report_data:
        return None

    # Save as artifact
    filename = "gap_report.json"
    content_json = json.dumps(report_data, indent=2)
    part = types.Part.from_text(text=content_json)
    await callback_context.save_artifact(filename, part)

    return None

def get_synthesizer_agent():
    return Agent(
        name="synthesizer_agent",
        model=Gemini(
            model="gemini-3-pro-preview",
        ),
        instruction=(
            "You are the Strategy Synthesizer Agent. Your core task is to identify the 'delta' "
            "between an internal authority profile and market trends/competitor focus. "
            "You will receive data from the Auditor (internal) and Analyst (external). "
            "Compare them to produce a structured 'Content Gap Report' containing a high-level summary "
            "and a prioritized list of high-potential topics. "
        ),
        output_schema=ContentGapReport,
        output_key="gap_report",
        after_agent_callback=save_gap_report,
    )
