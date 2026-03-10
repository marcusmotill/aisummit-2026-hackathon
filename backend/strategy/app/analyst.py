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
from google.adk.tools.google_search_tool import GoogleSearchTool
from typing import List

# Google Search has a 'one tool one agent' limitation. 
# We use bypass_multi_tools_limit=True to allow mixing it with other tools.
google_search = GoogleSearchTool(bypass_multi_tools_limit=True)

def analyze_competitor_focus(competitor_urls: List[str]) -> str:
    """Simulates analysis of competitor strategic focus based on their URLs.
    
    Args:
        competitor_urls: List of competitor website URLs.
        
    Returns:
        A summary of competitor focus areas.
    """
    # In a real scenario, this might crawl sitemaps or use a dedicated SEO API.
    # For the hackathon, we simulate this using search queries about competitors.
    results = []
    for url in competitor_urls:
        results.append(f"Competitor {url} appears focused on high-performance gear and sustainability initiatives.")
    
    return "\n".join(results)

def get_analyst_agent():
    return Agent(
        name="analyst_agent",
        model=Gemini(
            model="gemini-3-flash-preview",
        ),
        instruction=(
            "You are the Market Analyst Agent. Your goal is to identify trending search topics "
            "and competitor focus areas. Use `google_search` to find current trends and "
            "`analyze_competitor_focus` to understand what competitors are doing. "
            "Provide a report on high-potential keywords and strategic focus areas."
        ),
        tools=[google_search, analyze_competitor_focus],
    )
