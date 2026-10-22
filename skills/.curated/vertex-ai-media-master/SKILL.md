---
name: vertex-ai-media-master
description: 'Execute automatic activation for all google vertex ai multimodal operations
  operations. Use when appropriate context detected. Trigger with relevant phrases
  based on skill purpose.

  '
allowed-tools: Read, Write, Edit, Grep, Glob, Bash(general:*), Bash(util:*)
version: 2.26.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- productivity
- vertex-ai
compatibility: Designed for Claude Code
---
# Vertex AI Media Master

## Overview

Multimodal media operations on Google Cloud Vertex AI covering video understanding, audio generation, image creation, and marketing campaign automation. This skill orchestrates Gemini 2.5 Pro/Flash, Imagen 4, and Lyria models to process, analyze, and generate rich media assets.

## Prerequisites

- Google Cloud project with Vertex AI API enabled
- `google-cloud-aiplatform` Python SDK installed (`pip install google-cloud-aiplatform[vision,audio]`)
- `GOOGLE_CLOUD_PROJECT` and `GOOGLE_APPLICATION_CREDENTIALS` environment variables set
- Service account with `roles/aiplatform.user` permission
- Sufficient quota for target models (Gemini 2.5 Pro: 2M tokens/min; Imagen 4: 100 images/min)

## Instructions

1. Initialize the Vertex AI client with the target project and region (`us-central1` recommended for model availability).
2. Select the appropriate model for the task:
   - **Video analysis**: Gemini 2.5 Pro (up to 6 hours at low resolution, 2 hours at default).
   - **Image generation**: Imagen 4 for highest quality stills; Gemini 2.5 Flash Image for interleaved text+image output.
   - **Audio generation**: Lyria for music composition and background tracks.
   - **Campaign automation**: Gemini 2.5 Pro for multi-asset generation from a single prompt.
3. Prepare input media: upload source files to Cloud Storage (`gs://` URIs) or provide local paths for smaller assets.
4. Construct the generation request with explicit parameters (aspect ratio, duration, number of outputs, style constraints).
5. Execute the request and capture response objects containing generated media bytes or analysis text.
6. Post-process outputs: save generated images/audio to the target directory, extract structured insights from video analysis, or compile campaign asset bundles.
7. Validate results against brand guidelines or schema expectations before delivery.

## Output

- Generated image files (PNG/JPEG) from Imagen 4 or Gemini Flash Image
- Audio files (WAV/MP3) from Lyria model for background music, voiceovers, or sound effects
- Video analysis reports: scene breakdowns, key-moment timestamps, transcript text, marketing-insight summaries
- Campaign asset packages: hero images, social media graphics, ad copy, email marketing text, and video scripts
- Structured JSON metadata for each generated asset (model used, prompt, parameters, cost estimate)

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `PermissionDenied` on Vertex AI API | Service account lacks `aiplatform.user` role | Grant the required IAM role to the service account |
| `ResourceExhausted` / quota exceeded | Too many concurrent requests or token limit hit | Implement request batching; switch to Gemini 2.5 Flash for lower-cost operations |
| `InvalidArgument` on image generation | Prompt violates safety filters or unsupported aspect ratio | Revise the prompt to remove restricted content; use a supported aspect ratio (1:1, 16:9, 9:16) |
| Video processing timeout | Source video exceeds duration or resolution limits | Use low-resolution mode for videos over 2 hours; split longer videos into segments |
| Audio generation returns empty | Prompt too vague or duration parameter missing | Specify genre, tempo, mood, and an explicit duration in seconds |
| `NotFound` on model ID | Incorrect model name or model not available in region | Verify the model ID against current Vertex AI documentation; try `us-central1` |

## Examples

**Example 1: Analyze a competitor video ad**

- Input: A 60-second competitor video uploaded to `gs://bucket/competitor-ad.mp4`.
- Action: Send to Gemini 2.5 Pro with the prompt "Extract messaging themes, calls to action, visual style, and production techniques."
- Output: Structured analysis with timestamps for key scenes, identified CTAs, and a competitive positioning summary.

**Example 2: Generate campaign assets from a product brief**

- Input: Text brief describing a new product launch with target audience and brand guidelines.
- Action: Use Imagen 4 to generate 4 hero image variations, Lyria for a 30-second background track, and Gemini 2.5 Pro for ad copy in 3 languages.
- Output: Directory containing hero images, audio file, and a campaign-copy document organized by language.

**Example 3: Repurpose a long-form video into short-form clips**

- Input: A 10-minute product demo video.
- Action: Gemini 2.5 Pro identifies the three most engaging 15-second segments with scene-boundary timestamps.
- Output: Timestamp list with suggested captions for TikTok/Reels, plus a storyboard summary for each clip.

## Resources

- Detailed model capabilities and code patterns: [`references/core-capabilities.md`](references/core-capabilities.md)
- Vertex AI Multimodal overview: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/overview
- Imagen documentation: https://cloud.google.com/vertex-ai/generative-ai/docs/image/overview
- Video understanding guide: https://cloud.google.com/vertex-ai/generative-ai/docs/multimodal/video-understanding
- GenAI for Marketing reference repo: https://github.com/GoogleCloudPlatform/genai-for-marketing
