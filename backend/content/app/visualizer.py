import uuid
from typing import List, Dict, Any, Optional, Union
from google import genai
from google.genai import types
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import ToolContext

# Safety settings for image generation
SAFETY_SETTINGS = [
    types.SafetySetting(
        category="HARM_CATEGORY_HATE_SPEECH",
        threshold="BLOCK_LOW_AND_ABOVE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_LOW_AND_ABOVE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_HARASSMENT",
        threshold="BLOCK_LOW_AND_ABOVE",
    ),
    types.SafetySetting(
        category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
        threshold="BLOCK_LOW_AND_ABOVE",
    ),
]

async def generate_image(
    prompt: str,
    tool_context: ToolContext,
    aspect_ratio: str = "1:1",
    image_size: str = "1K",
    reference_images: Optional[List[str]] = None,
    enable_grounding: bool = False,
) -> Dict[str, Any]:
    """
    Generates or edits an image using Gemini 3.1 Flash Image.

    Args:
        prompt: The text prompt for image generation or editing instructions.
        tool_context: The tool context for artifact management.
        aspect_ratio: The aspect ratio of the generated image (Supported: 1:1, 3:2, 2:3, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9).
        image_size: The size of the generated image (e.g., "1K", "2K", "4K").
        reference_images: Optional list of artifact filenames to use as reference images.
        enable_grounding: Whether to enable Google Search grounding.

    Returns:
        Dict[str, Any]: A dictionary with 'filename' on success, or 'error' on failure.
    """
    try:
        # Project/Location implied from env
        client = genai.Client(location="global")

        contents: List[Union[str, types.Part]] = [prompt]
        if reference_images:
            for ref_file in reference_images:
                artifact = await tool_context.load_artifact(ref_file)
                if artifact and artifact.inline_data:
                    # Fix for load_artifact returning a Part directly or a wrapper
                    # The genai client expects Part or str
                    contents.append(artifact)
                else:
                    return {"error": f"Could not load reference image: {ref_file}"}

        tools = [{"google_search": {}}] if enable_grounding else None

        response = await client.aio.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=contents,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio,
                    image_size=image_size,
                ),
                tools=tools,
                safety_settings=SAFETY_SETTINGS,
            ),
        )

        if not response.parts:
            return {"error": "No parts returned in response"}

        for part in response.parts:
            if part.inline_data:
                filename = f"image_{uuid.uuid4().hex[:8]}.png"
                await tool_context.save_artifact(filename, part)
                return {"filename": filename}

        return {"error": "No image generated in response parts"}
    except Exception as e:
        return {"error": str(e)}

def search_brand_library(query: str) -> List[str]:
    """Simulates searching a brand library for relevant imagery.
    
    Args:
        query: Search query for visuals.
        
    Returns:
        List of relevant image descriptions or mock paths.
    """
    return [
        f"Mock internal image: High-quality photo of {query} in a sustainability context.",
        f"Mock internal illustration: Graphic representing {query} values."
    ]

def get_visualizer_agent():
    return Agent(
        name="visualizer_agent",
        model=Gemini(
            model="gemini-3-flash-preview",
        ),
        instruction=(
            "You are the Visual Asset Agent. Your goal is to suggest or create visual accompaniments "
            "for text-based campaign assets. "
            "\n\nWorkflow:"
            "\n1. Search the 'brand library' for existing assets first via `search_brand_library`."
            "\n2. If nothing fits perfectly, use `generate_image` to create a brand-aligned visual. "
            "Ensure the prompt is detailed and premium. Use `aspect_ratio='16:9'` for blog headers and `'9:16'` for social stories."
            "\n3. Ensure all visuals maintain a premium, 'wow' aesthetic consistent with the brand."
        ),
        tools=[search_brand_library, generate_image],
    )
