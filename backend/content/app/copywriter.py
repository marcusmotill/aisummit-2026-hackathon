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
from typing import List

def generate_social_copy(platform: str, themes: List[str], tone: str = "professional") -> str:
    """Generates social media copy based on provided themes and platform specs.
    
    Args:
        platform: The social media platform (e.g., 'Twitter', 'LinkedIn', 'Instagram').
        themes: List of themes to incorporate.
        tone: The desired tone of voice.
        
    Returns:
        Generated copy for the specified platform.
    """
    # Simulated tool for copy generation
    return f"Simulated {platform} copy based on themes: {', '.join(themes)} with a {tone} tone."

def get_copywriter_agent():
    return Agent(
        name="copywriter_agent",
        model=Gemini(
            model="gemini-3-flash-preview",
        ),
        instruction=(
            "You are the Multi-Channel Copywriter Agent. Your goal is to take deconstructed themes "
            "and quotes and transform them into platform-specific assets. "
            "\n\nPlatforms to support:"
            "\n- Twitter (X): Short, punchy, thread-ready."
            "\n- LinkedIn: Professional, value-driven, engagement-focused."
            "\n- Email: Conversational, clear CTA."
            "\n- Instagram/Ads: Visual-first, concise hooks."
            "\n\nAlways maintain the brand's unique voice across all channels."
        ),
        tools=[generate_social_copy],
    )
