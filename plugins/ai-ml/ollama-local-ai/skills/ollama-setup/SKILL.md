---
name: ollama-setup
description: 'Configure auto-configure Ollama when user needs local LLM deployment,
  free AI alternatives,

  or wants to eliminate hosted API costs. Trigger phrases: "install ollama",

  "local AI", "free LLM", "self-hosted AI", "replace OpenAI", "no API costs". Use
  when appropriate context detected. Trigger with relevant phrases based on skill
  purpose.

  '
allowed-tools: Read, Write, Bash(cmd:*)
version: 1.19.0
author: Jeremy Longshore <jeremy@intentsolutions.io>
license: MIT
tags:
- ai
- deployment
- api
- llm
compatibility: Designed for Claude Code
---
# Ollama Setup

## Overview

Auto-configure Ollama for local LLM deployment, eliminating hosted API costs and enabling offline AI inference. This skill handles system assessment, model selection based on available hardware (RAM, GPU), installation across macOS/Linux/Docker, and integration with Python, Node.js, and REST API clients.

## Prerequisites

- macOS 12+, Linux (Ubuntu 20.04+, Fedora 36+), or Docker runtime
- Minimum 8 GB RAM for 7B parameter models; 16 GB for 13B models; 32 GB+ for 70B models
- Optional: NVIDIA GPU with CUDA drivers for accelerated inference (`nvidia-smi` to verify)
- Optional: Apple Silicon (M1/M2/M3) for Metal-accelerated inference on macOS
- Disk space: 4-40 GB depending on model size (quantized weights)
- Package manager: `brew` (macOS), `curl` (Linux), or `docker` (containerized)

## Instructions

1. Detect the host operating system and available hardware using `uname -s`, `free -h` (Linux) or `vm_stat` (macOS), and `nvidia-smi` (if GPU present)
2. Select appropriate models based on available RAM:
   - **8 GB**: llama3.2:7b (4 GB), mistral:7b (4 GB), phi3:14b (8 GB)
   - **16 GB**: codellama:13b (7 GB), mixtral:8x7b (26 GB quantized)
   - **32 GB+**: llama3.2:70b (40 GB), codellama:34b (20 GB)
3. Install Ollama using the platform-appropriate method:
   - macOS: `brew install ollama && brew services start ollama`
   - Linux: `curl -fsSL https://ollama.com/install.sh | sh && sudo systemctl start ollama`
   - Docker: `docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama`
4. Pull the recommended model: `ollama pull llama3.2`
5. Verify the installation by listing available models (`ollama list`) and running a test prompt (`ollama run llama3.2 "Say hello"`)
6. Confirm the REST API is accessible: `curl http://localhost:11434/api/tags`
7. Configure integration with the target application using the appropriate client library (Python `ollama`, Node.js `ollama`, or raw HTTP)
8. Set up GPU acceleration if NVIDIA or Apple Silicon hardware is detected
9. Configure model persistence and cache directory if non-default storage location is required
10. Validate end-to-end inference latency and throughput for the selected model

See [`references/skill-workflow.md`](references/skill-workflow.md) for the detailed workflow with code snippets.

## Output

- Ollama installation confirmed and running as a system service or Docker container
- Selected model(s) pulled and cached locally with verified inference capability
- REST API endpoint accessible at `http://localhost:11434`
- Integration code snippet for the target language (Python, Node.js, or cURL)
- Hardware assessment report: OS, RAM, GPU availability, recommended models
- Performance baseline: tokens per second for the selected model on local hardware

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `ollama: command not found` | Installation incomplete or PATH not updated | Re-run install script; restart shell session; verify `/usr/local/bin/ollama` exists |
| Model pull fails with timeout | Network connectivity issue or Ollama registry unreachable | Check internet connection; retry with `ollama pull --insecure` behind corporate proxy |
| Out of memory during inference | Model size exceeds available RAM | Switch to a smaller quantized model (e.g., 7B instead of 13B); close memory-intensive applications |
| GPU not detected | CUDA drivers missing or incompatible version | Install CUDA toolkit >= 11.8; verify with `nvidia-smi`; restart Ollama service after driver install |
| Port 11434 already in use | Another service occupying the default Ollama port | Stop conflicting service; or set `OLLAMA_HOST=0.0.0.0:11435` environment variable |

See [`references/errors.md`](references/errors.md) for additional error scenarios.

## Examples

**Scenario 1: Developer Workstation Setup** -- Install Ollama on a macOS M2 machine with 16 GB RAM. Pull codellama:13b for code generation tasks. Integrate with a Python FastAPI application using the `ollama` Python package. Expected throughput: 30-50 tokens/second on Apple Silicon.

**Scenario 2: Air-Gapped Server Deployment** -- Install Ollama on an offline Ubuntu server via pre-downloaded binary. Transfer model weights via USB. Configure as a systemd service with auto-restart. Serve llama3.2:7b via REST API for internal team use.

**Scenario 3: Docker-Based CI Pipeline** -- Run Ollama in a Docker container as part of a CI/CD pipeline for automated code review. Pull mistral:7b, expose the API on port 11434, and integrate with a Node.js test harness that sends code diffs for analysis.

## Resources

- [Ollama Official Documentation](https://ollama.com) -- installation, model library, API reference
- [Ollama Model Library](https://ollama.com/library) -- available models with size and capability details
- [Ollama Python Client](https://github.com/ollama/ollama-python) -- Python SDK for local inference
- [Ollama JavaScript Client](https://github.com/ollama/ollama-js) -- Node.js SDK for local inference
- Hardware sizing guide: RAM requirements by model parameter count and quantization level
