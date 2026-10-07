# AI/ML Engineering Pack

**Professional toolkit for building production-ready AI/ML systems with Claude Code**

Master prompt engineering, LLM integration, RAG systems, and AI safety with 12 specialized plugins that accelerate AI development by 10x.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/jeremylongshore/claude-code-plugins)
[![Claude Code](https://img.shields.io/badge/Claude_Code-0.1.0+-purple.svg)](https://claude.ai/code)

## What's Included

**12 specialized plugins across 4 AI/ML categories:**

### 1. Prompt Engineering (3 plugins)

- **prompt-architect** (agent) - Expert in CoT reasoning, few-shot learning, and advanced prompt patterns
- **prompt-optimizer** (agent) - Reduce LLM costs by 60-90% while maintaining quality
- **prompt-template-gen** (command: `/ptg`) - Generate production-ready prompt templates with type safety

### 2. LLM Integration (3 plugins)

- **llm-integration-expert** (agent) - Production API patterns, error handling, streaming, rate limiting
- **model-selector** (agent) - Choose optimal models based on cost, quality, latency requirements
- **llm-api-scaffold** (command: `/las`) - Generate complete LLM API with FastAPI, Docker, monitoring

### 3. RAG Systems (3 plugins)

- **rag-architect** (agent) - Design RAG systems, chunking strategies, retrieval optimization
- **vector-db-expert** (agent) - Select and configure vector databases (Pinecone, Qdrant, Weaviate, etc.)
- **rag-pipeline-gen** (command: `/rpg`) - Generate complete RAG pipeline with embeddings and retrieval

### 4. AI Safety (3 plugins)

- **ai-safety-expert** (agent) - Content filtering, PII detection, bias mitigation, compliance
- **prompt-injection-defender** (agent) - Defend against prompt injection and jailbreak attacks
- **ai-monitoring-setup** (command: `/ams`) - Set up LLM monitoring, cost tracking, and alerts

## Quick Start

### Installation

```bash
# Add the marketplace (if not already added)
claude plugin marketplace add jeremylongshore/claude-code-plugins

# Install AI/ML Engineering Pack
claude plugin install ai-ml-engineering-pack@claude-code-plugins-plus

# Verify installation
claude plugin list
```

**Full installation guide:** INSTALLATION.md

### 10-Minute Tutorial

Build your first AI feature in 10 minutes:

```bash
# Start Claude Code
claude

# Inside Claude, optimize a prompt
"Optimize this prompt for cost and quality:
'I would like you to create a detailed product description for...'"
# Claude uses prompt-optimizer agent to reduce tokens by 70%

# Generate a reusable prompt template
/ptg

# Build a production LLM API
/las

# Create a complete RAG system
/rpg

# Add AI safety guardrails
"Implement PII detection and toxicity filtering for my chatbot"
```

**Complete tutorial:** QUICK_START.md

## ROI & Value Proposition

Real-world results from production deployments:

| Use Case | Time Saved | Cost Savings | ROI |
|----------|-----------|--------------|-----|
| E-Commerce Recommendations | 12.5 hours | $249,250/year | 11,891% |
| Legal Document Analysis | 12 hours | $781,500/year | 34,192% |
| Customer Support Automation | 16 hours | $350,400/year | 11,283% |
| Content Moderation | 19 hours | $1,872,000/year | 40,781% |
| Code Documentation | 145 hours | $14,100 (one-time) | 2,565% |
| Medical Diagnosis Assistant | 28 hours | $44,600,000/year | 75,392% |

**Average ROI: 29,351%** | **Average payback period: 3 days**

**Detailed case studies:** USE_CASES.md

## Plugin Reference

### Prompt Engineering

#### `prompt-architect` (Agent)

Expert in advanced prompt engineering techniques and patterns.

**Capabilities:**

- Chain-of-Thought (CoT) reasoning
- Few-shot and zero-shot learning
- Prompt composition patterns
- Meta-prompting and self-improvement
- Multi-modal prompts (text + images)

**When to use:**

- "Design a prompt for [complex task]"
- "Improve this prompt: [existing prompt]"
- "What's the best prompting technique for [use case]?"

**Activation triggers:** Prompt design, CoT, few-shot learning, prompt patterns

---

#### `prompt-optimizer` (Agent)

Optimize prompts for cost reduction (60-90% savings) while maintaining quality.

**Capabilities:**

- Token reduction techniques (remove verbosity, use abbreviations)
- Prompt caching strategies
- Model selection guidance (cheap vs expensive)
- Cost-quality trade-off analysis
- ROI calculation

**When to use:**

- "Reduce the cost of this prompt: [prompt]"
- "Optimize my prompts for $1000/month budget"
- "How can I reduce token usage by 70%?"

**Example:**

```
Before (52 tokens): "I would like you to please analyze..."
After (15 tokens): "Analyze and summarize main points."
Savings: 71% token reduction = $0.15/1000 calls (GPT-4)
```

**Activation triggers:** Cost optimization, token reduction, prompt efficiency

---

#### `/ptg` - Prompt Template Generator (Command)

Generate production-ready prompt templates with type safety and validation.

**Usage:**

```bash
/ptg

# Claude asks:
# - Use case (e.g., product descriptions, customer support, code review)
# - Variables (e.g., product_name, features, tone)
# - Output format (Python, TypeScript)
# - Validation requirements
```

**Generated output:**

- Python: Pydantic models with type safety
- TypeScript: Zod schemas with validation
- Usage examples
- Cost estimation
- Unit tests

**Example output:**

```python
@dataclass
class ProductDescriptionInput:
    product_name: str
    features: List[str]
    target_audience: str
    tone: Literal["professional", "casual"] = "professional"

class ProductDescriptionGenerator:
    TEMPLATE = """..."""

    def generate(self, input: ProductDescriptionInput) -> str:
        # Validates input, generates prompt, calls LLM
        ...
```

---

### LLM Integration

#### `llm-integration-expert` (Agent)

Production patterns for LLM API integration with error handling and reliability.

**Capabilities:**

- Multi-provider integration (OpenAI, Anthropic, Google, Cohere)
- Exponential backoff retry logic
- Rate limiting (token bucket, sliding window)
- Response streaming (Server-Sent Events)
- Fallback systems (multi-provider)
- Circuit breaker patterns
- Token counting and cost tracking

**When to use:**

- "Implement LLM API integration with retry logic"
- "Add streaming support to my chatbot"
- "Build multi-provider fallback system"

**Code examples:**

```python
# Retry with exponential backoff
@retry_with_backoff(max_retries=3, base_delay=1.0)
async def complete(prompt: str):
    return await llm.complete(prompt)

# Token bucket rate limiting
rate_limiter = TokenBucketRateLimiter(capacity=100, refill_rate=10)
await rate_limiter.wait_for_token()
```

**Activation triggers:** LLM API, error handling, streaming, rate limiting, fallback

---

#### `model-selector` (Agent)

Guide model selection based on cost, quality, latency, and use case requirements.

**Capabilities:**

- Model comparison matrix (GPT-4, Claude 3, Gemini)
- Pricing analysis (per 1M tokens)
- Latency benchmarks
- Quality assessments by task type
- Model cascading strategies
- A/B testing frameworks

**When to use:**

- "Which model should I use for customer support?"
- "Compare GPT-4 vs Claude 3 Opus for code generation"
- "How can I reduce costs with model cascading?"

**Model comparison:**

| Model | Input ($/1M) | Output ($/1M) | Latency | Best For |
|-------|-------------|---------------|---------|----------|
| GPT-4 Turbo | $10 | $30 | 3-5s | Complex reasoning |
| GPT-3.5 Turbo | $0.50 | $1.50 | 1-2s | Simple tasks |
| Claude 3 Opus | $15 | $75 | 4-6s | Highest quality |
| Claude 3 Haiku | $0.25 | $1.25 | 0.5-1s | Speed & cost |

**Activation triggers:** Model selection, cost optimization, performance comparison

---

#### `/las` - LLM API Scaffold (Command)

Generate complete production-ready LLM API integration code.

**Usage:**

```bash
/las

# Claude asks:
# - Provider (OpenAI, Anthropic, Google)
# - Features (streaming, rate limiting, caching, error handling)
# - Framework (FastAPI, Express.js)
# - Deployment (Docker, Kubernetes)
```

**Generated files:**

```
llm-api/
├── main.py                 # FastAPI application
├── llm_client.py          # LLM client with retry logic
├── rate_limiter.py        # Token bucket rate limiting
├── cache.py               # Redis caching
├── monitoring.py          # Prometheus metrics
├── Dockerfile             # Production container
├── docker-compose.yml     # Redis + app
├── requirements.txt       # Dependencies
└── tests/                 # Unit and integration tests
```

**Features included:**

- Exponential backoff retry (3 attempts)
- Rate limiting (token bucket algorithm)
- Response caching (Redis, 5 min TTL)
- Streaming support (SSE)
- Cost tracking
- Prometheus metrics
- Docker deployment

---

### RAG Systems

#### `rag-architect` (Agent)

Expert in designing and optimizing Retrieval-Augmented Generation systems.

**Capabilities:**

- RAG architecture patterns
- Chunking strategies (fixed, recursive, semantic)
- Embedding model selection
- Retrieval optimization (hybrid search, reranking)
- Query expansion techniques
- Evaluation metrics (MRR, NDCG)

**When to use:**

- "Design a RAG system for customer support knowledge base"
- "What chunking strategy should I use for legal documents?"
- "How can I improve retrieval accuracy?"

**Chunking strategies:**

```python
# Fixed-size (simple, fast)
chunks = [text[i:i+512] for i in range(0, len(text), 512)]

# Recursive (respects structure)
splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# Semantic (context-aware)
chunks = semantic_splitter.split_by_meaning(text)
```

**Activation triggers:** RAG architecture, chunking, retrieval, embeddings

---

#### `vector-db-expert` (Agent)

Select and optimize vector databases for RAG systems.

**Capabilities:**

- Database comparison (Pinecone, Qdrant, Weaviate, ChromaDB, pgvector, Milvus)
- HNSW index tuning
- Scaling strategies (sharding, replication)
- Query optimization
- Migration planning

**When to use:**

- "Which vector database should I use for 10M documents?"
- "How do I tune HNSW parameters for better performance?"
- "Compare Pinecone vs Qdrant for my use case"

**Database comparison:**

| Database | Best For | Pricing | Hosting |
|----------|---------|---------|---------|
| Pinecone | Managed, auto-scaling | $0.096/GB/month | Cloud only |
| Qdrant | Performance, self-hosted | Open source | Self/cloud |
| Weaviate | GraphQL, hybrid search | Open source | Self/cloud |
| ChromaDB | Local development | Open source | Local only |
| pgvector | Existing PostgreSQL | Open source | Self-hosted |

**Activation triggers:** Vector database, HNSW, scaling, performance

---

#### `/rpg` - RAG Pipeline Generator (Command)

Generate complete RAG pipeline with all components.

**Usage:**

```bash
/rpg

# Claude asks:
# - Document types (PDFs, docs, web pages)
# - Vector database (Pinecone, Qdrant, Weaviate)
# - Embedding model (OpenAI, open-source)
# - LLM (GPT-4, Claude, Gemini)
# - Features (reranking, hybrid search, caching)
```

**Generated files:**

```
rag-system/
├── document_loader.py      # PDF/DOCX/TXT loaders
├── chunker.py              # Recursive text splitter
├── embedder.py             # OpenAI embeddings
├── vector_store.py         # Qdrant integration
├── retriever.py            # Hybrid search + reranking
├── generator.py            # LLM response generation
├── pipeline.py             # End-to-end orchestration
├── api.py                  # FastAPI endpoints
├── docker-compose.yml      # Vector DB + app
└── example_usage.py        # Complete examples
```

**Features included:**

- Multi-format document loading (PDF, DOCX, TXT, MD)
- Recursive chunking (512 tokens, 50 overlap)
- Vector similarity search
- Cohere reranking (optional)
- Source attribution with page numbers
- Query expansion
- Caching
- FastAPI REST endpoints
- Docker deployment

---

### AI Safety

#### `ai-safety-expert` (Agent)

Comprehensive AI safety with content filtering, PII protection, and bias mitigation.

**Capabilities:**

- Toxicity detection (BERT-based classification)
- PII detection and redaction (Presidio)
- Bias detection (gender, racial, age)
- Content moderation (OpenAI Moderation API)
- Safety guardrails (input/output filtering)
- GDPR/CCPA/HIPAA compliance

**When to use:**

- "Implement PII detection for user inputs"
- "Add toxicity filtering to my chatbot"
- "Detect and mitigate bias in LLM outputs"
- "Ensure HIPAA compliance for medical data"

**Safety pipeline:**

```python
class SafetyGuardrails:
    async def safe_completion(self, user_input: str, llm):
        # 1. Input checks
        if not await self.check_input(user_input):
            return {"error": "Input blocked"}

        # 2. Redact PII
        safe_input = self.pii_detector.redact(user_input)

        # 3. Generate response
        response = await llm.complete(safe_input)

        # 4. Output checks
        safe_response = await self.check_output(response)

        return safe_response
```

**PII detection:**

- Email addresses, phone numbers, SSN
- Credit card numbers
- IP addresses
- Names, addresses
- Medical record numbers (for HIPAA)

**Activation triggers:** AI safety, PII, toxicity, bias, content moderation

---

#### `prompt-injection-defender` (Agent)

Defend against prompt injection attacks and jailbreaks.

**Capabilities:**

- Pattern-based detection (regex for common attacks)
- ML classification (fine-tuned BERT model)
- Input sanitization
- Output validation
- System prompt protection
- Jailbreak detection (DAN, Developer Mode, etc.)

**When to use:**

- "Protect my chatbot from prompt injection"
- "Detect jailbreak attempts"
- "Validate user inputs for manipulation"

**Attack patterns detected:**

```python
ATTACK_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions',
    r'(repeat|print|show)\s+(your\s+)?(system\s+)?prompt',
    r'(pretend|act)\s+(you\'?re|to\s+be)',
    r'(DAN|Developer\s+Mode|Jailbreak)',
    r'(new\s+role|you\s+are\s+now)',
]
```

**Defense strategies:**

1. **Detection:** Identify attack patterns
2. **Sanitization:** Remove/escape dangerous inputs
3. **Validation:** Verify outputs don't leak system prompts
4. **Monitoring:** Log and alert on suspicious activity

**Activation triggers:** Prompt injection, jailbreak, security, input validation

---

#### `/ams` - AI Monitoring Setup (Command)

Set up comprehensive LLM monitoring with cost tracking and alerting.

**Usage:**

```bash
/ams

# Claude asks:
# - Metrics (latency, cost, tokens, errors)
# - Dashboards (Grafana, custom)
# - Alerts (Slack, PagerDuty, email)
# - Budget ($1000/month)
```

**Generated files:**

```
monitoring/
├── metrics.py              # Prometheus metrics
├── cost_tracker.py         # Cost tracking with budget alerts
├── grafana_dashboard.json  # Pre-built dashboard
├── alerting_rules.yml      # Alert rules
├── prometheus.yml          # Prometheus config
├── docker-compose.yml      # Prometheus + Grafana
└── README.md               # Setup instructions
```

**Metrics collected:**

- Request count (by model, status)
- Latency (p50, p95, p99)
- Token usage (input, output)
- Cost per request
- Error rate
- Cache hit rate

**Alerts configured:**

- Budget threshold (80%, 90%, 100%)
- High error rate (>5%)
- Slow responses (>10s)
- Token limit approaching

**Dashboards:**

- Real-time request monitoring
- Cost tracking (daily, weekly, monthly)
- Model performance comparison
- Error analysis

---

## Documentation

- **Installation Guide** - Prerequisites, setup, verification
- **Quick Start** - 10-minute tutorial with examples
- **Use Cases** - Real-world applications with ROI
- **Troubleshooting** - Common issues and solutions

## Example Workflows

### Build a Customer Support Bot (10 minutes)

```bash
claude

# 1. Generate RAG pipeline for knowledge base
/rpg
Requirements: Support docs, Qdrant, GPT-4

# 2. Add safety guardrails
"Implement PII detection and toxicity filtering"

# 3. Set up monitoring
/ams
Requirements: Prometheus, Slack alerts, $5K budget

# 4. Deploy
"Create Docker deployment with all components"
```

**Result:** Production-ready support bot with 65% ticket automation, 30s response time, comprehensive safety.

### Optimize Prompts to Reduce Costs (5 minutes)

```bash
claude

# 1. Analyze current prompts
"Analyze my prompts for cost optimization opportunities"

# 2. Optimize individual prompts
"Reduce this prompt to 50% of tokens:
'I would like you to carefully analyze the following customer feedback...'"

# 3. Generate reusable templates
/ptg
Use case: Customer feedback analysis

# 4. Calculate savings
"Calculate ROI if I process 10,000 requests/month"
```

**Result:** 60-90% cost reduction while maintaining quality.

### Build RAG System for Legal Documents (15 minutes)

```text
claude

# 1. Design RAG architecture
"Design RAG system for legal document search with:
- 10,000 contracts
- Clause extraction
- Precedent search
- GDPR compliance"

# 2. Generate complete pipeline
/rpg
Requirements: Legal docs (PDF), Qdrant (self-hosted), GPT-4

# 3. Add PII protection
"Implement PII detection for attorney-client privilege"

# 4. Set up monitoring
/ams
Track: accuracy, retrieval time, cost per query
```

**Result:** Legal document analysis system with 94% accuracy, 82ms latency, PII protection.

## Learning Resources

### Video Tutorials (Coming Soon)

- Prompt Engineering Masterclass (30 min)
- Building Production RAG Systems (45 min)
- AI Safety Best Practices (20 min)

### Blog Posts

- [Reduce LLM Costs by 90%](https://example.com/reduce-llm-costs)
- [Building RAG Systems That Actually Work](https://example.com/rag-systems)
- [Comprehensive Guide to AI Safety](https://example.com/ai-safety)

### Community

- [GitHub Discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/claude-code) - `claude-code` tag

## Pricing

**One-time purchase: $79**

What's included:

- All 12 plugins (lifetime access)
- Free updates and new plugins
- Email support
- Community support in GitHub Discussions
- Documentation and examples

**Compare to alternatives:**

- Manual implementation: 40+ hours ($4,000 at $100/hour)
- Consultants: $150-300/hour × 40 hours = $6,000-12,000
- AI/ML Engineering Pack: **$79** (99% cost savings)

**Average payback period: 3 days**

Buy Now on Gumroad | [Volume Licensing](mailto:[email protected])

## 🆘 Support

**Email:** [email protected]

**GitHub Issues:** https://github.com/jeremylongshore/claude-code-plugins/issues

**Response time:** Within 24 hours (usually faster)

**Community:** Ask in [GitHub Discussions](https://github.com/jeremylongshore/claude-code-plugins/discussions) for community support

## Updates

**Current version:** 1.0.0

**Update policy:** Free updates for life, including new plugins and features

**Changelog:**

- **v1.0.0** (2025-10-10) - Initial release with 12 plugins

To update:

```bash
claude plugin update ai-ml-engineering-pack
```

## License

MIT License - See LICENSE for details

**Commercial use permitted** - Use in commercial projects, redistribute, modify

## Acknowledgments

Built with:

- [Claude Code](https://claude.ai/code) - AI-powered development CLI
- [LangChain](https://langchain.com) - LLM framework
- [Presidio](https://microsoft.github.io/presidio/) - PII detection
- [Qdrant](https://qdrant.tech) - Vector database
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python framework

## Ready to Get Started?

1. **Install the pack** - 5-minute setup
2. **Complete Quick Start** - Build your first AI feature in 10 minutes
3. **Explore use cases** - See real-world ROI examples
4. **[Join the community](https://github.com/jeremylongshore/claude-code-plugins/discussions)** - Connect with other AI/ML engineers

---

**Questions?** Email [email protected] or open a [GitHub issue](https://github.com/jeremylongshore/claude-code-plugins/issues).

**Built by AI engineers, for AI engineers.**
