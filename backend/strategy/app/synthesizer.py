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

from google.adk.agents import Agent
from google.adk.models import Gemini

def get_synthesizer_agent():
    return Agent(
        name="synthesizer_agent",
        model=Gemini(
            model="gemini-3-pro-preview", # Use Pro for synthesis/comparative logic
        ),
        instruction=(
            "You are the Strategy Synthesizer Agent. Your core task is to identify the 'delta' "
            "between an internal authority profile and market trends/competitor focus. "
            "You will receive data from the Auditor (internal) and Analyst (external). "
            "Compare them to produce a 'Content Gap Report'—a prioritized list of high-potential "
            "topics to create content for. Format your output as a Markdown table."
        ),
        tools=[], # Uses reasoning/synthesis rather than external tools
    )
