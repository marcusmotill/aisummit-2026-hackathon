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
import requests
import re
from typing import List, Dict

def audit_sitemap(url: str) -> str:
    """Parses a sitemap and clusters URLs by their path structure to identify content sections.
    
    Args:
        url: The URL of the sitemap (xml).
        
    Returns:
        A formatted string summarizing the content clusters found.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return f"Failed to fetch sitemap: {response.status_code}"
        
        # Simple regex to extract loc tags
        urls = re.findall(r'<loc>(.*?)</loc>', response.text)
        if not urls:
            return "No URLs found in sitemap."
        
        clusters: Dict[str, List[str]] = {}
        for u in urls:
            # Extract the first path segment as a cluster name
            match = re.search(r'https?://[^/]+/([^/]+)', u)
            cluster_name = match.group(1) if match else "root"
            if cluster_name not in clusters:
                clusters[cluster_name] = []
            clusters[cluster_name].append(u)
            
        summary = "Sitemap Audit Results:\n"
        for name, cluster_urls in clusters.items():
            summary += f"- Cluster: /{name} ({len(cluster_urls)} URLs)\n"
            # Show top 3 samples
            for sample in cluster_urls[:3]:
                summary += f"  - {sample}\n"
        
        return summary
    except Exception as e:
        return f"Error auditing sitemap: {str(e)}"

def sample_cluster_content(urls: List[str]) -> str:
    """Samples content from a list of URLs and provides a thematic summary.
    
    Args:
        urls: A list of URLs to sample from.
        
    Returns:
        A thematic summary of the sampled content.
    """
    # Sample up to 3 URLs
    samples = urls[:3]
    results = []
    for u in samples:
        try:
            response = requests.get(u, timeout=10)
            if response.status_code == 200:
                # Basic cleanup: remove scripts and styles using regex
                text = re.sub(r'<(script|style).*?>.*?</\1>', '', response.text, flags=re.DOTALL | re.IGNORECASE)
                # Remove other HTML tags
                text = re.sub(r'<.*?>', ' ', text)
                # Collapse whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                results.append(f"Content from {u}:\n{text[:2000]}...") # Truncate for efficiency
            else:
                results.append(f"Failed to fetch {u}: {response.status_code}")
        except Exception as e:
            results.append(f"Error fetching {u}: {str(e)}")
        
    return "\n\n".join(results)

def get_auditor_agent():
    return Agent(
        name="auditor_agent",
        model=Gemini(
            model="gemini-3-flash-preview",
        ),
        instruction=(
            "You are the Internal Auditor Agent. Your goal is to establish a thematic authority profile "
            "of a target website. Use the `audit_sitemap` tool to understand the site structure, and "
            "`sample_cluster_content` to understand what the content is actually about. "
            "Summarize your findings into a 'Thematic Authority Profile' JSON."
        ),
        tools=[audit_sitemap, sample_cluster_content],
    )
