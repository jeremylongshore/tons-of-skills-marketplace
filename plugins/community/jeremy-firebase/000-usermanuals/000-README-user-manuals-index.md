# User Manuals Index - jeremy-firebase Plugin

**Created:** November 13, 2025
**Purpose:** Master index and navigation guide for all user manuals and supplemental documentation
**Status:** Active Development

---

## Overview

This directory contains comprehensive user manuals and supplemental reference documentation for the **jeremy-firebase plugin**. These manuals are derived from official Google Cloud Platform tutorials and enhanced with practical examples, cross-references to related plugins, and production deployment guidance.

---

## Quick Navigation

### Core Tutorial Manuals (001-004)

| Manual | Title | Topic | Difficulty | Time |
|--------|-------|-------|------------|------|
| **001** | [Vertex AI A2A Protocol Tutorial](001-vertex-ai-a2a-protocol-tutorial.md) | Agent-to-Agent communication on Agent Engine | Intermediate | 30-45 min |
| **002** | [ADK Sessions & Memory for Cloud Run](002-adk-sessions-memory-cloud-run.md) | Persistent sessions and long-term memory | Intermediate | 30-45 min |
| **003** | [Agent Engine Terraform Deployment](003-agent-engine-terraform-deployment.md) | Infrastructure as Code for agents | Intermediate-Advanced | 60-90 min |
| **004** | [Gemini Supervised Fine-Tuning](004-gemini-supervised-fine-tuning-predictive-maintenance.md) | Domain-specific model adaptation | Advanced | 2-4 hours |

### Reference Documentation (005-008)

| Doc | Title | Purpose |
|-----|-------|---------|
| **005** | [External Reference Links Index](005-external-reference-links-index.md) | Comprehensive index of all external documentation sources |
| **006** | [ADK & Agent Engine Reference](006-supplemental-adk-agent-engine-reference.md) | Deep dive into ADK architecture and Agent Engine services |
| **007** | [Cloud Run & Gemini Tuning Reference](007-supplemental-cloud-run-gemini-tuning-reference.md) | Deployment platforms and model customization |
| **008** | [Vertex AI Search & Ray Comprehensive Guide](008-vertex-ai-search-and-ray-comprehensive-guide.md) | Enterprise search, RAG applications, and distributed ML workloads |

---

## Learning Path Recommendations

### Path 1: Agent Development Basics

**Goal:** Build and deploy your first ADK agent

1. **Start:** Manual 001 - A2A Protocol Tutorial
   - Understand Agent Engine fundamentals
   - Learn about A2A protocol
   - Deploy simple Q&A agent

2. **Next:** Manual 002 - Sessions & Memory
   - Add persistent conversations
   - Implement long-term memory
   - Deploy to Cloud Run with UI

3. **Reference:** Doc 006 - ADK Reference
   - Deep dive into ADK components
   - Understand tools and workflows
   - Learn best practices

**Outcome:** Production-ready agent with memory deployed on Cloud Run

---

### Path 2: Infrastructure as Code

**Goal:** Automate agent deployment with Terraform

1. **Start:** Manual 003 - Terraform Deployment
   - Package agents with cloudpickle
   - Write Terraform configurations
   - Deploy to Agent Engine

2. **Reference:** Doc 007 - Cloud Run Reference
   - Understand deployment options
   - Learn scaling strategies
   - Configure production settings

**Outcome:** Repeatable, version-controlled agent deployments

---

### Path 3: Model Customization

**Goal:** Fine-tune Gemini for domain-specific tasks

1. **Start:** Manual 004 - Supervised Fine-Tuning
   - Prepare training datasets
   - Launch fine-tuning jobs
   - Evaluate tuned models

2. **Reference:** Doc 007 - Gemini Tuning Reference
   - Understand adapter sizes
   - Learn data format requirements
   - Follow best practices

**Outcome:** Custom Gemini model optimized for your use case

---

### Path 4: Enterprise Search & RAG Applications

**Goal:** Build Google-quality search with RAG capabilities

1. **Start:** Doc 008 - Vertex AI Search Overview
   - Understand data store types
   - Learn about structured vs unstructured data
   - Explore blended search capabilities

2. **Next:** Doc 008 - RAG with Vertex AI Search and Gemini
   - Implement retrieval augmented generation
   - Ground LLM responses in enterprise data
   - Build multimodal RAG applications

3. **Reference:** Doc 008 - Vector Search vs Vertex AI Search
   - Choose the right search solution
   - Understand when to use each
   - Combine both for optimal results

**Outcome:** Production-ready enterprise search with generative AI answer generation

---

### Path 5: Distributed ML at Scale

**Goal:** Run large-scale ML workloads with Ray on Vertex AI

1. **Start:** Doc 008 - Ray on Vertex AI Overview
   - Understand Ray architecture
   - Learn about cluster connectivity
   - Configure autoscaling

2. **Next:** Doc 008 - Distributed ML Workloads with Ray
   - Distributed training with Ray Train
   - Hyperparameter tuning with Ray Tune
   - Batch inference at scale

3. **Practice:** Doc 008 - BigQuery Integration with Ray
   - Read data from BigQuery
   - Transform with Ray Data
   - Write results back to BigQuery

**Outcome:** Scalable ML pipelines with distributed computing

---

## Manual Summaries

### 001: Vertex AI A2A Protocol Tutorial

**Source:** `agents/agent_engine/tutorial_a2a_on_agent_engine.ipynb`

**What You'll Learn:**

- Building A2A-compliant agents with ADK
- Deploying to fully-managed Agent Engine
- Querying agents via SDK, A2A Client, and HTTP
- Local testing before cloud deployment

**Key Concepts:**

- **A2A Protocol:** Open standard for agent communication
- **Agent Cards:** Capability discovery mechanism
- **Agent Executor:** Task lifecycle management (submitted → working → completed)
- **Agent Engine:** Serverless platform for agent hosting

**Practical Examples:**

- Q&A agent with web search
- Three query methods demonstrated
- Local testing workflow

**Related Plugins:**

- jeremy-vertex-engine
- jeremy-adk-orchestrator
- jeremy-vertex-validator
- jeremy-gcp-starter-examples

---

### 002: ADK Sessions & Memory for Cloud Run

**Source:** `agents/cloud_run/agents_with_memory/get_started_with_memory_for_adk_in_cloud_run.ipynb`

**What You'll Learn:**

- Implementing short-term memory (Sessions)
- Implementing long-term memory (Memory Bank)
- Deploying ADK agents to Cloud Run
- Using PreloadMemoryTool and after_agent_callback

**Key Concepts:**

- **Sessions:** Multi-turn conversation history
- **Memory Bank:** Persistent, personalized memories
- **VertexAiSessionService:** Production-ready session storage
- **VertexAiMemoryBankService:** Managed memory persistence

**Practical Examples:**

- Weather agent with memory
- Session creation and management
- Memory generation and retrieval
- Cloud Run deployment with ADK CLI

**Architecture:**

```
User Request → Cloud Run Service → ADK Runner
                                    ├── Session Service (short-term)
                                    ├── Memory Service (long-term)
                                    └── Agent
                                         ├── PreloadMemoryTool (fetch)
                                         └── after_agent_callback (save)
```

**Related Plugins:**

- jeremy-adk-orchestrator
- jeremy-vertex-engine
- jeremy-vertex-validator
- jeremy-genkit-terraform

---

### 003: Agent Engine Terraform Deployment

**Source:** `agents/agent_engine/tutorial_get_started_with_agent_engine_terraform_deployment.ipynb`

**What You'll Learn:**

- Agent Engine template pattern (\_\_init\_\_, set_up, query)
- Packaging agents with cloudpickle
- Writing Terraform configurations for agents
- Deploying custom and ADK agents
- Managing dependencies and requirements

**Key Concepts:**

- **Infrastructure as Code (IaC):** Version-controlled deployments
- **Reasoning Engine Resource:** Terraform resource for Agent Engine
- **Agent Template Pattern:** Python class structure
- **Class Methods:** Operations exposed by agent (query, async_stream_query, etc.)

**Practical Examples:**

1. **Custom Agent:** Simple Gemini-powered assistant
2. **ADK Agent:** Currency exchange agent with function calling

**Terraform Workflow:**

```
1. Build Agent (Python class)
2. Package Agent (cloudpickle → .pkl)
3. Upload to Cloud Storage (.pkl, requirements.txt, dependencies.tar.gz)
4. Deploy with Terraform (google_vertex_ai_reasoning_engine)
5. Query Agent (Vertex AI SDK)
```

**Related Plugins:**

- jeremy-vertex-terraform
- jeremy-adk-terraform
- jeremy-vertex-engine
- jeremy-adk-orchestrator

---

### 004: Gemini Supervised Fine-Tuning for Predictive Maintenance

**Source:** `gemini/tuning/sft_gemini_predictive_maintenance.ipynb`

**What You'll Learn:**

- Supervised fine-tuning workflow
- Preparing JSONL training data
- Launching and monitoring tuning jobs
- Evaluating tuned models
- Integrating Gemini for reporting

**Key Concepts:**

- **Supervised Fine-Tuning:** Adapt model weights with labeled data
- **JSONL Format:** Training data structure (user/model pairs)
- **Adapter Sizes:** Control tuning capacity vs. speed
- **Validation Dataset:** Monitor training progress

**Use Case:**
Equipment status classification (Normal, Warning, Critical) based on sensor data

**Workflow:**

```
1. Generate/Load Data (sensor readings, failure logs)
2. Prepare Tuning Data (JSONL format)
3. Upload to GCS (train, validation, test splits)
4. Launch Fine-Tuning Job (google-genai SDK)
5. Monitor Job (poll status every minute)
6. Evaluate Tuned Model (qualitative comparison)
7. Generate Summary (Gemini-powered reporting)
```

**Dataset Requirements:**

- Max training tokens per example: 131,072
- Max validation dataset: 5,000 examples
- Max file size: 1GB (JSONL)
- Max dataset size: 1M text-only or 300K multimodal examples

**Related Plugins:**

- jeremy-vertex-engine
- jeremy-vertex-validator
- jeremy-genkit-pro
- jeremy-firebase

---

## Supplemental Documentation Summaries

### 005: External Reference Links Index

**Purpose:** Comprehensive index of all external documentation sources

**Coverage:**

- 25+ unique documentation sources
- GitHub repositories (GoogleCloudPlatform/generative-ai)
- Official Google Cloud documentation
- Terraform registry resources
- External APIs (Frankfurter currency exchange)

**Categories:**

- Google Cloud Platform Services (Vertex AI, Cloud Run, BigQuery)
- Developer Tools & SDKs (ADK, Terraform, Google GenAI SDK)
- GitHub Repositories (source notebooks)
- External APIs

---

### 006: ADK & Agent Engine Supplemental Reference

**Purpose:** Consolidated deep-dive into ADK and Agent Engine architecture

**Sections:**

1. **Agent Development Kit Overview**
   - What is ADK and why use it
   - Core components (agents, tools, sessions, memory)
   - Runtime and deployment options
   - Key differentiators

2. **Vertex AI Agent Engine Overview**
   - Core services (runtime, evaluation, sessions, memory, code execution)
   - Supported frameworks (LangChain, ADK, LlamaIndex, etc.)
   - Deployment paths (Agent Starter Pack, manual)
   - Enterprise security features

3. **Memory Bank Deep Dive**
   - Memory generation process
   - Storage and retrieval mechanisms
   - Integration with ADK agents
   - Use cases and best practices

**Key Insights:**

- ADK is model-agnostic and deployment-agnostic
- Agent Engine provides fully-managed serverless infrastructure
- Memory Bank enables personalization across sessions
- Three integration tiers for different frameworks

---

### 007: Cloud Run & Gemini Tuning Supplemental Reference

**Purpose:** Comprehensive guide to deployment platforms and model customization

**Sections:**

1. **Cloud Run Overview**
   - Three execution models (Services, Jobs, Worker Pools)
   - Key features (auto-scaling, pay-per-use, disposable containers)
   - Integration ecosystem
   - ADK deployment to Cloud Run

2. **Gemini Supervised Fine-Tuning**
   - When to use fine-tuning
   - Supported models (Gemini 2.x family)
   - Key use cases (classification, summarization, QA, chat)
   - Technical specifications

3. **Fine-Tuning Workflow**
   - Data preparation (JSONL format)
   - Upload to Cloud Storage
   - Launch and monitor jobs
   - Evaluation and deployment

**Key Insights:**

- Cloud Run supports any containerized application
- Scale to zero = cost-effective serverless
- Fine-tuning excels for consistent output formatting
- Tuned models use same pricing as base models

---

### 008: Vertex AI Search & Ray Comprehensive Guide

**Purpose:** Master guide for enterprise search, RAG applications, and distributed ML workloads

**Sections:**

1. **Vertex AI Search Overview**
   - What it is and core capabilities
   - Application types (custom search, media, healthcare, website)
   - Key features (NLP, ranking, generative AI)
   - Data ingestion methods

2. **Data Store Types and Architecture**
   - Structured data stores (BigQuery, JSON)
   - Unstructured data stores (PDFs, documents, images)
   - Website data stores (domain verification, advanced indexing)
   - Media and healthcare data stores
   - Blended search (multi-data store apps)

3. **RAG with Vertex AI Search and Gemini**
   - Retrieval Augmented Generation workflow
   - Grounding LLM responses in enterprise data
   - Multimodal RAG (text + images)
   - Grounding with Google Search

4. **Vector Search vs Vertex AI Search**
   - Comparison matrix and use cases
   - When to use each solution
   - Combining both for optimal results

5. **Ray on Vertex AI Overview**
   - What Ray is and why use it on Vertex AI
   - Cluster architecture and connectivity models
   - Key features (persistent resources, autoscaling, monitoring)

6. **Distributed ML Workloads with Ray**
   - Distributed training (XGBoost, PyTorch, Gemma fine-tuning)
   - Hyperparameter tuning with Ray Tune
   - Batch inference at scale

7. **BigQuery Integration with Ray**
   - Reading from BigQuery tables
   - Writing results back to BigQuery
   - End-to-end ML pipelines

8. **Production Deployment Patterns**
   - Development → Staging → Production workflow
   - Ephemeral clusters for batch jobs
   - Persistent clusters with job scheduling
   - Cost optimization strategies

**Key Insights:**

- Vertex AI Search provides out-of-the-box NLP and ranking
- RAG grounds LLM responses in enterprise data to reduce hallucinations
- Multimodal RAG combines text and visual data for richer context
- Ray on Vertex AI enables distributed computing with minimal code changes
- BigQuery integration allows seamless data pipelines
- Autoscaling and spot instances optimize costs

---

## Cross-Reference Matrix

### Manual → Plugin Mapping

| Manual | jeremy-vertex-engine | jeremy-adk-orchestrator | jeremy-vertex-validator | jeremy-genkit-pro | jeremy-vertex-terraform |
|--------|---------------------|-------------------------|-------------------------|-------------------|------------------------|
| **001: A2A Protocol** | ✅ Deployment | ✅ A2A Protocol | ✅ Validation | ⚠️ Partial | ⚠️ Partial |
| **002: Sessions & Memory** | ✅ Agent Engine | ✅ Memory Bank | ✅ Validation | ✅ Integration | ⚠️ Partial |
| **003: Terraform** | ✅ Deployment | ⚠️ Partial | ✅ Validation | ⚠️ Partial | ✅ IaC |
| **004: Fine-Tuning** | ✅ Gemini | ⚠️ Partial | ✅ Validation | ✅ Gemini | ✅ IaC |

**Legend:**

- ✅ Directly relevant
- ⚠️ Partially relevant
- ❌ Not relevant

---

## Practical Integration Examples

### Example 1: ADK Agent with Memory on Cloud Run

**Use Manual 002 + Doc 006 + Doc 007**

```python
# 1. Create agent with memory tools (Manual 002)
from google.adk.agents import Agent
from google.adk.tools.preload_memory_tool import PreloadMemoryTool

agent = Agent(
    name="customer_support_agent",
    model="gemini-2.5-flash",
    tools=[handle_inquiry, PreloadMemoryTool()],
    after_agent_callback=add_session_to_memory
)

# 2. Deploy to Cloud Run (Doc 007)
adk deploy cloud_run --project PROJECT_ID --region us-central1 \
    --service_name support-agent \
    --session_service_uri=agentengine://AGENT_ENGINE_ID \
    --memory_service_uri=agentengine://AGENT_ENGINE_ID \
    --with_ui
```

---

### Example 2: Terraform-Deployed ADK Agent with Fine-Tuned Model

**Use Manual 003 + Manual 004 + Doc 007**

```python
# 1. Fine-tune Gemini (Manual 004)
tuning_job = vertex_client.tunings.tune(
    base_model="gemini-2.5-flash",
    training_dataset={"gcs_uri": "gs://bucket/customer_support_data.jsonl"},
    config={"adapter_size": "ADAPTER_SIZE_FOUR", "epoch_count": 3}
)

# 2. Create ADK agent with tuned model
agent = Agent(
    name="support_agent",
    model=tuning_job.tuned_model.endpoint,  # ← Use tuned model
    tools=[resolve_ticket, search_knowledge_base]
)

# 3. Deploy with Terraform (Manual 003)
# Write main.tf with google_vertex_ai_reasoning_engine resource
terraform init
terraform apply
```

---

### Example 3: Multi-Agent System with A2A Protocol

**Use Manual 001 + jeremy-adk-orchestrator plugin**

```python
# 1. Create specialized agents
research_agent = Agent(name="research", tools=[web_search])
analysis_agent = Agent(name="analysis", tools=[data_analysis])
reporting_agent = Agent(name="reporting", tools=[generate_report])

# 2. Deploy to Agent Engine (Manual 001)
for agent in [research_agent, analysis_agent, reporting_agent]:
    client.agent_engines.create(agent=agent)

# 3. Orchestrate via A2A protocol (jeremy-adk-orchestrator)
supervisor = create_supervisor_agent(
    sub_agents=[research_agent, analysis_agent, reporting_agent]
)
```

---

## Next Steps

### For New Users

1. **Read Manual 001** to understand Agent Engine basics
2. **Complete Manual 002** to add memory capabilities
3. **Reference Doc 006** for deep understanding
4. **Deploy your first agent** using ADK CLI

### For Infrastructure Teams

1. **Read Manual 003** for Terraform deployment
2. **Reference Doc 007** for Cloud Run configuration
3. **Set up CI/CD pipelines** with GitHub Actions
4. **Use jeremy-vertex-terraform plugin** for automation

### For ML Engineers

1. **Read Manual 004** for fine-tuning workflow
2. **Reference Doc 007** for tuning best practices
3. **Prepare high-quality training data**
4. **Evaluate tuned models** before production

### For Enterprise Search Teams

1. **Read Doc 008** - Vertex AI Search Overview
2. **Explore Doc 008** - Data Store Types and RAG
3. **Implement blended search** across multiple data sources
4. **Deploy with jeremy-vertex-terraform plugin**

### For Data Scientists & ML Researchers

1. **Read Doc 008** - Ray on Vertex AI Overview
2. **Practice Doc 008** - Distributed ML Workloads
3. **Integrate with BigQuery** for large-scale data processing
4. **Scale experiments** with Ray Tune hyperparameter optimization

---

## Additional Resources

### Official Documentation

- **ADK Documentation:** https://google.github.io/adk-docs/
- **Vertex AI Agent Engine:** https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/overview
- **Vertex AI Search:** https://cloud.google.com/generative-ai-app-builder/docs/introduction
- **Ray on Vertex AI:** https://cloud.google.com/vertex-ai/docs/open-source/ray-on-vertex-ai/overview
- **Vector Search:** https://cloud.google.com/vertex-ai/docs/vector-search/overview
- **Cloud Run Documentation:** https://cloud.google.com/run/docs
- **Terraform Registry:** https://registry.terraform.io/providers/hashicorp/google/latest/docs

### GitHub Repositories

- **GoogleCloudPlatform/generative-ai:** https://github.com/GoogleCloudPlatform/generative-ai
- **Agent Starter Pack:** https://github.com/GoogleCloudPlatform/agent-starter-pack

### Community

- **GitHub Discussions:** https://github.com/jeremylongshore/claude-code-plugins/discussions

---

## Document Maintenance

### Update Frequency

- **Core Manuals (001-004):** Updated when source notebooks change
- **Reference Docs (005-008):** Updated quarterly or when APIs change
- **This Index:** Updated with each new manual addition

### Contributing

Found an error or want to suggest improvements? Open an issue at:
https://github.com/jeremylongshore/claude-code-plugins/issues

---

**Version:** 2.0.0
**Last Updated:** November 13, 2025
**Status:** Active Development
**Total Manuals:** 8 documents (4 tutorials + 4 references)
**Latest Addition:** Manual 008 - Vertex AI Search & Ray Comprehensive Guide
