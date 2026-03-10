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

from google.adk.agents import Agent
from google.adk.models import Gemini
from typing import List, Dict

def extract_core_themes(draft_content: str) -> Dict:
    """Extracts core themes, key arguments, and pull-quotes from a content draft.
    
    Args:
        draft_content: The full text of the content draft.
        
    Returns:
        A dictionary containing categorized content assets.
    """
    # This is a specialized tool that the agent can use to structure its output.
    # The LLM will perform the actual analysis based on its instructions.
    return {
        "status": "ready_for_deconstruction",
        "instruction": "Analyze the provided text and identify: 1) Three core themes, 2) Three key arguments, and 3) Three high-impact pull-quotes."
    }

def get_deconstructor_agent():
    return Agent(
        name="deconstructor_agent",
        model=Gemini(
            model="gemini-3-flash-preview",
        ),
        instruction=(
            "You are the Content Deconstructor Agent. Your goal is to take a long-form content draft "
            "and break it down into atomic, reusable components. "
            "\n\nTasks:"
            "\n1. Identify the core themes (the 'big ideas')."
            "\n2. Extract the strongest arguments or data points."
            "\n3. Select high-impact pull-quotes that represent the brand voice."
            "\n\nProvide your analysis in a structured JSON format that can be used by downstream copywriters."
        ),
        tools=[extract_core_themes],
    )
