# Phase 2: Campaign Generation Design Spec

## Objective
Automate the deconstruction of a drafted blog post into a multi-channel content campaign ("Campaign-in-a-Box").

## Components

### 1. Content Deconstructor
Examines a long-form draft and returns structured themes.
- Input: `draft_content` (Markdown/Text)
- Logic: Identifies logical sections, unique arguments, and emotional hooks.

### 2. Multi-Channel Copywriter
Generates tailored assets.
- Platforms: Twitter (X), LinkedIn, Email, Meta Ads.
- Tone: Matches the source content but adapts to platform norms (e.g., emojis on LinkedIn, brevity on Twitter).

### 3. Visual Asset Agent
Provides visual context.
- Method: Uses LLM to generate descriptive prompts or "search" a mock library.
- Integration: For the hackathon, we will simulate a call to an image model or return a descriptive metadata object for the image.

## Orchestration Strategy
The root agent will use `AgentTool` to invoke each specialist. 
1. Deconstructor runs first to provide the context.
2. Copywriter and Visual Asset Agent can run in parallel (or sequentially if the Visual Agent needs the specific copy).
