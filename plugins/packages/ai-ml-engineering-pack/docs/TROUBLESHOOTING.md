# AI/ML Engineering Pack - Troubleshooting Guide

Common issues and solutions when using the AI/ML Engineering Pack.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [API Key & Authentication](#api-key--authentication)
3. [LLM Integration Problems](#llm-integration-problems)
4. [RAG System Issues](#rag-system-issues)
5. [Vector Database Errors](#vector-database-errors)
6. [Safety Pipeline Problems](#safety-pipeline-problems)
7. [Performance Issues](#performance-issues)
8. [Cost Management](#cost-management)
9. [Monitoring & Debugging](#monitoring--debugging)
10. [Getting Help](#getting-help)

---

## Installation Issues

### Issue: "Plugin not found" after installation

**Symptoms:**

```bash
claude plugin install ai-ml-engineering-pack@claude-code-plugins-plus
Error: Plugin 'ai-ml-engineering-pack' not found in marketplace 'claude-code-plugins-plus'
```

**Solutions:**

1. **Verify marketplace is added:**

```bash
claude plugin marketplace list
# Should show: jeremylongshore/claude-code-plugins
```

1. **Add marketplace if missing:**

```bash
claude plugin marketplace add jeremylongshore/claude-code-plugins
```

1. **Update marketplace index:**

```bash
claude plugin marketplace update claude-code-plugins-plus
```

1. **Check Claude Code version:**

```bash
claude --version
# Requires >= 0.1.0
```

### Issue: Commands not showing up (e.g., `/ptg` doesn't work)

**Symptoms:**

- Type `/ptg` and nothing happens
- Commands don't appear in autocomplete

**Solutions:**

1. **Reload Claude Code session:**

```bash
# Exit and restart Claude Code
exit
claude
```

1. **Verify plugin is active:**

```bash
claude plugin list
# All plugins should show  (active)
```

1. **Reinstall the pack:**

```bash
claude plugin uninstall ai-ml-engineering-pack
claude plugin install ai-ml-engineering-pack@claude-code-plugins-plus
```

---

## API Key & Authentication

### Issue: "Invalid API key" errors

**Symptoms:**

```python
openai.AuthenticationError: Incorrect API key provided
```

**Solutions:**

1. **Check API key format:**

```bash
# OpenAI keys start with 'sk-'
echo $OPENAI_API_KEY
# Should output: sk-...

# Anthropic keys start with 'sk-ant-'
echo $ANTHROPIC_API_KEY
# Should output: sk-ant-...
```

1. **Set environment variables correctly:**

```bash
# In .env file:
OPENAI_API_KEY=sk-your-actual-key-here
ANTHROPIC_API_KEY=sk-ant-your-actual-key-here
GOOGLE_API_KEY=your-google-key-here

# Load .env:
export $(cat .env | xargs)
```

1. **Test API keys directly:**

```bash
# OpenAI
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Anthropic
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"
```

1. **Check API key permissions:**

- OpenAI: Ensure key has access to required models (GPT-4, embeddings)
- Anthropic: Verify Claude 3 models are enabled
- Google: Enable Vertex AI API in GCP console

### Issue: Rate limit errors

**Symptoms:**

```python
openai.RateLimitError: Rate limit exceeded
```

**Solutions:**

1. **Implement rate limiting in generated code:**

```python
# Add to your config:
from llm_integration import TokenBucketRateLimiter

rate_limiter = TokenBucketRateLimiter(
    capacity=100,  # Max 100 requests
    refill_rate=10  # 10 requests per second
)
```

1. **Request rate limit increase:**

- OpenAI: https://platform.openai.com/account/rate-limits
- Anthropic: Contact support for tier upgrade

1. **Use model cascading to reduce high-tier usage:**

```python
# Try cheap model first, fallback to expensive
try:
    response = await client.complete(model="gpt-3.5-turbo", ...)
except Exception:
    response = await client.complete(model="gpt-4-turbo", ...)
```

---

## LLM Integration Problems

### Issue: Slow response times (>30 seconds)

**Symptoms:**

- LLM calls taking 30+ seconds
- Timeout errors

**Solutions:**

1. **Enable streaming:**

```python
# Instead of:
response = await client.complete(prompt)

# Use streaming:
async for chunk in await client.complete_stream(prompt):
    print(chunk, end="")
```

1. **Reduce token count:**

```python
# Use prompt-optimizer to reduce tokens:
# Before: 500 tokens → After: 150 tokens (70% reduction)
max_tokens=200  # Limit output length
```

1. **Use faster models:**

```python
# Slow: gpt-4-turbo (5-10s)
# Fast: gpt-3.5-turbo (1-2s)
# Faster: claude-3-haiku (0.5-1s)
```

1. **Check network latency:**

```bash
# Test API latency
time curl -X POST https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{"model":"gpt-3.5-turbo","messages":[{"role":"user","content":"Hi"}]}'
```

### Issue: "Context length exceeded" errors

**Symptoms:**

```python
openai.BadRequestError: This model's maximum context length is 4096 tokens
```

**Solutions:**

1. **Count tokens before sending:**

```python
import tiktoken

def count_tokens(text: str, model: str = "gpt-4") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Check before calling:
if count_tokens(prompt) > 4000:
    prompt = truncate_prompt(prompt, max_tokens=4000)
```

1. **Use models with larger context:**

```python
# Small context (4K tokens)
model="gpt-3.5-turbo"

# Large context (128K tokens)
model="gpt-4-turbo"
model="claude-3-opus"  # 200K tokens
```

1. **Implement prompt truncation:**

```python
def truncate_to_token_limit(text: str, max_tokens: int = 4000):
    encoding = tiktoken.encoding_for_model("gpt-4")
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return encoding.decode(tokens)
```

### Issue: Inconsistent outputs (different results each time)

**Symptoms:**

- Same prompt produces different outputs
- Unpredictable quality

**Solutions:**

1. **Lower temperature:**

```python
# High variance (temperature=1.0)
# Low variance (temperature=0.1)
response = await client.complete(
    prompt=prompt,
    temperature=0.1  # More deterministic
)
```

1. **Set seed (for reproducibility):**

```python
# OpenAI supports seed parameter
response = await client.complete(
    prompt=prompt,
    seed=42  # Same seed = same output
)
```

1. **Use few-shot examples:**

```python
# Add examples to stabilize outputs
prompt = f"""
Example 1: Input: ... Output: ...
Example 2: Input: ... Output: ...

Now process: {user_input}
"""
```

---

## RAG System Issues

### Issue: Poor retrieval quality (irrelevant results)

**Symptoms:**

- RAG returns documents unrelated to query
- Answers are generic, not using context

**Solutions:**

1. **Improve chunking strategy:**

```python
# Bad: Fixed 500-char chunks (splits mid-sentence)
chunks = [text[i:i+500] for i in range(0, len(text), 500)]

# Good: Recursive character splitting (respects sentences)
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=512,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""]
)
chunks = splitter.split_text(text)
```

1. **Add metadata filters:**

```python
# Filter by document type, date, category
results = await vector_store.search(
    query_embedding,
    top_k=10,
    filter={
        "document_type": "user_guide",
        "last_updated": {"$gte": "2024-01-01"}
    }
)
```

1. **Implement reranking:**

```python
# After vector search, rerank with Cohere
from cohere import Client

cohere = Client(api_key=os.getenv("COHERE_API_KEY"))

# Get 20 candidates from vector search
candidates = await vector_store.search(query, top_k=20)

# Rerank to top 5
reranked = cohere.rerank(
    query=query,
    documents=[c.text for c in candidates],
    top_n=5
)

final_results = [candidates[r.index] for r in reranked.results]
```

1. **Use hybrid search (vector + keyword):**

```python
# Combine vector similarity with BM25 keyword search
from rank_bm25 import BM25Okapi

bm25_results = bm25.get_top_n(query, corpus, n=20)
vector_results = await vector_store.search(query, top_k=20)

# Merge and rerank
combined = merge_results(bm25_results, vector_results)
```

### Issue: Embedding model errors

**Symptoms:**

```python
openai.APIError: Model 'text-embedding-ada-002' not found
```

**Solutions:**

1. **Use correct embedding model names:**

```python
# OpenAI embeddings (current)
model="text-embedding-3-small"  # $0.02/1M tokens
model="text-embedding-3-large"  # $0.13/1M tokens

# Legacy (still works)
model="text-embedding-ada-002"  # $0.10/1M tokens
```

1. **Handle embedding errors:**

```python
async def embed_with_retry(text: str, max_retries: int = 3):
    for attempt in range(max_retries):
        try:
            return await embedder.embed(text)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)
```

1. **Batch embeddings for efficiency:**

```python
# Bad: Embed one at a time (slow, expensive)
embeddings = [await embedder.embed(chunk) for chunk in chunks]

# Good: Batch embed (10x faster)
embeddings = await embedder.embed_batch(chunks, batch_size=100)
```

---

## Vector Database Errors

### Issue: "Connection refused" to Qdrant/Pinecone/Weaviate

**Symptoms:**

```python
ConnectionError: Failed to connect to Qdrant at localhost:6333
```

**Solutions:**

1. **Verify database is running:**

**Qdrant (local):**

```bash
docker ps | grep qdrant
# If not running:
docker run -p 6333:6333 qdrant/qdrant
```

**Pinecone (cloud):**

```bash
# Test API connectivity
curl https://api.pinecone.io/describe_index_stats \
  -H "Api-Key: YOUR_PINECONE_API_KEY"
```

**Weaviate (local):**

```bash
docker-compose up -d weaviate
```

1. **Check connection settings:**

```python
# Qdrant
from qdrant_client import QdrantClient

client = QdrantClient(
    url="http://localhost:6333",  # Check URL
    timeout=30  # Increase timeout if network is slow
)

# Pinecone
import pinecone

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="us-west1-gcp"  # Check region
)
```

1. **Test connection manually:**

```bash
# Qdrant
curl http://localhost:6333/collections

# Pinecone
curl https://controller.YOUR_ENV.pinecone.io/describe_index_stats \
  -H "Api-Key: YOUR_KEY"
```

### Issue: "Collection not found" errors

**Symptoms:**

```python
ValueError: Collection 'my-rag-collection' does not exist
```

**Solutions:**

1. **Create collection before using:**

```python
# Check if collection exists
collections = client.get_collections()
if "my-rag-collection" not in [c.name for c in collections.collections]:
    # Create collection
    client.create_collection(
        collection_name="my-rag-collection",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )
```

1. **Verify vector dimensions match:**

```python
# Embedding size must match collection config
# text-embedding-3-small: 1536 dimensions
# text-embedding-3-large: 3072 dimensions

client.create_collection(
    collection_name="my-rag-collection",
    vectors_config=VectorParams(
        size=1536,  # Must match embedding model
        distance=Distance.COSINE
    )
)
```

### Issue: Slow vector search (>5 seconds)

**Symptoms:**

- Vector similarity search taking 5+ seconds
- Query timeouts

**Solutions:**

1. **Tune HNSW index parameters:**

```python
# Better performance (less accuracy)
client.create_collection(
    collection_name="my-collection",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    hnsw_config=HnswConfigDiff(
        m=16,  # Default: 16 (increase for better recall)
        ef_construct=100,  # Default: 100 (build-time quality)
        full_scan_threshold=10000  # Use index above this size
    )
)

# Query-time parameters
results = client.search(
    collection_name="my-collection",
    query_vector=embedding,
    limit=10,
    search_params=SearchParams(
        hnsw_ef=128  # Higher = more accurate but slower
    )
)
```

1. **Add payload index for filters:**

```python
# Index frequently filtered fields
client.create_payload_index(
    collection_name="my-collection",
    field_name="document_type",
    field_schema="keyword"
)
```

1. **Use quantization (Qdrant):**

```python
# Reduce memory and improve speed with scalar quantization
client.update_collection(
    collection_name="my-collection",
    quantization_config=ScalarQuantization(
        scalar=ScalarQuantizationConfig(
            type=ScalarType.INT8,  # 4x memory reduction
            quantile=0.99
        )
    )
)
```

---

## Safety Pipeline Problems

### Issue: PII detector not finding obvious PII

**Symptoms:**

```python
text = "Call me at 555-123-4567"
detected = pii_detector.detect_pii(text)
# Returns: [] (empty)
```

**Solutions:**

1. **Check entity types configuration:**

```python
# Specify entity types explicitly
detected = pii_detector.detect_pii(
    text,
    entities=["PHONE_NUMBER", "EMAIL_ADDRESS", "PERSON", "SSN"]
)
```

1. **Lower detection threshold:**

```python
from presidio_analyzer import AnalyzerEngine

analyzer = AnalyzerEngine()
results = analyzer.analyze(
    text=text,
    language="en",
    score_threshold=0.5  # Default: 0.6 (lower = more sensitive)
)
```

1. **Use regex fallback for common patterns:**

```python
import re

class HybridPIIDetector:
    REGEX_PATTERNS = {
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b'
    }

    def detect(self, text: str):
        # Try Presidio first
        presidio_results = self.presidio.detect(text)

        # Fallback to regex
        regex_results = {}
        for entity_type, pattern in self.REGEX_PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                regex_results[entity_type] = matches

        return self.merge_results(presidio_results, regex_results)
```

### Issue: Toxicity filter too aggressive (false positives)

**Symptoms:**

- Benign messages flagged as toxic
- Can't discuss certain topics (medical, legal)

**Solutions:**

1. **Increase toxicity threshold:**

```python
# Default threshold: 0.7
# Higher = less sensitive
toxicity_filter = ToxicityFilter(threshold=0.85)
```

1. **Add context-aware filtering:**

```python
def is_toxic_in_context(text: str, context: str) -> bool:
    # Check if text is toxic standalone
    base_toxicity = toxicity_model(text)[0]["score"]

    # Check with context
    contextual_toxicity = toxicity_model(f"{context}\n{text}")[0]["score"]

    # Use contextual score (more accurate)
    return contextual_toxicity > threshold
```

1. **Whitelist specific terms for domain:**

```python
# Medical terms that may trigger false positives
MEDICAL_WHITELIST = ["cancer", "tumor", "pain", "bleeding", "death"]

def filter_with_whitelist(text: str, whitelist: List[str]) -> bool:
    # Remove whitelisted terms temporarily
    cleaned_text = text
    for term in whitelist:
        cleaned_text = cleaned_text.replace(term, "[MEDICAL_TERM]")

    return toxicity_model(cleaned_text)[0]["score"] > threshold
```

---

## Performance Issues

### Issue: High memory usage during processing

**Symptoms:**

- Python process using 8GB+ RAM
- Out of memory errors

**Solutions:**

1. **Use generators for large datasets:**

```python
# Bad: Load all documents into memory
documents = [load_doc(file) for file in files]
embeddings = embedder.embed_batch(documents)

# Good: Process in batches with generator
def document_generator(files, batch_size=100):
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        yield [load_doc(file) for file in batch]

for batch in document_generator(files):
    embeddings = embedder.embed_batch(batch)
    vector_store.upsert(embeddings)
```

1. **Clear caches periodically:**

```python
import gc

# After processing large batch
gc.collect()

# Or use context manager
with tempfile.TemporaryDirectory() as tmpdir:
    # Process files
    pass  # Automatically cleaned up
```

1. **Reduce model size:**

```python
# Use quantized models (4-bit, 8-bit)
from transformers import AutoModelForSequenceClassification

model = AutoModelForSequenceClassification.from_pretrained(
    "unitary/toxic-bert",
    load_in_8bit=True  # 4x memory reduction
)
```

### Issue: Slow batch processing

**Symptoms:**

- Processing 1000 documents takes hours
- CPU usage low (<20%)

**Solutions:**

1. **Use async parallel processing:**

```python
import asyncio

# Bad: Sequential processing (slow)
results = [await process(doc) for doc in documents]

# Good: Parallel with semaphore (control concurrency)
async def process_batch(documents, max_concurrent=10):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def process_with_limit(doc):
        async with semaphore:
            return await process(doc)

    return await asyncio.gather(*[process_with_limit(doc) for doc in documents])

results = await process_batch(documents, max_concurrent=20)
```

1. **Use multiprocessing for CPU-bound tasks:**

```python
from multiprocessing import Pool

# CPU-bound: text preprocessing, embedding
def process_document(doc):
    return embedder.embed(doc)

with Pool(processes=8) as pool:
    results = pool.map(process_document, documents)
```

1. **Implement caching:**

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=1000)
def embed_cached(text: str):
    return embedder.embed(text)

# Or use Redis for distributed caching
import redis

redis_client = redis.Redis(host='localhost', port=6379)

def embed_with_redis_cache(text: str):
    cache_key = hashlib.md5(text.encode()).hexdigest()
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    embedding = embedder.embed(text)
    redis_client.setex(cache_key, 3600, json.dumps(embedding))  # 1 hour TTL
    return embedding
```

---

## Cost Management

### Issue: Unexpectedly high API costs

**Symptoms:**

- Monthly bill is $5K (expected $500)
- Budget alerts firing daily

**Solutions:**

1. **Implement cost tracking:**

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CostTracker:
    monthly_budget: float = 1000.0

    PRICING = {
        "gpt-4-turbo": {"input": 10.00, "output": 30.00},  # per 1M tokens
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50}
    }

    def log_request(self, model: str, input_tokens: int, output_tokens: int):
        cost = (
            (input_tokens / 1_000_000) * self.PRICING[model]["input"] +
            (output_tokens / 1_000_000) * self.PRICING[model]["output"]
        )

        self.current_cost += cost

        # Alert if approaching budget
        if self.current_cost > self.monthly_budget * 0.8:
            self.send_alert(f"80% of monthly budget used: ${self.current_cost:.2f}")

        return cost
```

1. **Use model cascading:**

```python
async def smart_completion(prompt: str, complexity: str = "auto"):
    # Determine complexity
    if complexity == "auto":
        complexity = await classify_complexity(prompt)

    # Route to appropriate model
    if complexity == "simple":
        return await llm.complete(model="gpt-3.5-turbo", prompt=prompt)  # $0.0015/1K
    else:
        return await llm.complete(model="gpt-4-turbo", prompt=prompt)  # $0.01/1K

# Savings: 85% if 70% of queries are simple
```

1. **Cache aggressively:**

```python
# Cache LLM responses
@lru_cache(maxsize=10000)
def cached_completion(prompt: str, model: str):
    return llm.complete(prompt=prompt, model=model)

# Cache embeddings (most expensive at scale)
def cached_embedding(text: str):
    # Use Redis with long TTL
    cache_key = f"emb:{hashlib.md5(text.encode()).hexdigest()}"
    cached = redis_client.get(cache_key)

    if cached:
        return json.loads(cached)

    embedding = embedder.embed(text)
    redis_client.setex(cache_key, 86400 * 7, json.dumps(embedding))  # 7 days
    return embedding
```

1. **Set hard limits:**

```python
class BudgetEnforcer:
    def __init__(self, daily_limit: float = 100.0):
        self.daily_limit = daily_limit
        self.daily_spend = 0.0
        self.last_reset = datetime.now().date()

    async def check_budget(self):
        # Reset daily counter
        if datetime.now().date() > self.last_reset:
            self.daily_spend = 0.0
            self.last_reset = datetime.now().date()

        if self.daily_spend >= self.daily_limit:
            raise BudgetExceededError(f"Daily budget of ${self.daily_limit} exceeded")

    async def complete(self, prompt: str, model: str):
        await self.check_budget()

        response = await llm.complete(prompt=prompt, model=model)
        cost = calculate_cost(response.usage)

        self.daily_spend += cost
        return response
```

---

## Monitoring & Debugging

### Issue: Can't debug why LLM responses are poor quality

**Symptoms:**

- LLM gives irrelevant answers
- No visibility into decision-making

**Solutions:**

1. **Add detailed logging:**

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def complete_with_logging(prompt: str, model: str):
    logger.info(f"Sending prompt to {model}")
    logger.debug(f"Prompt (first 200 chars): {prompt[:200]}")

    start_time = time.time()
    response = await llm.complete(prompt=prompt, model=model)
    latency = time.time() - start_time

    logger.info(f"Received response in {latency:.2f}s")
    logger.debug(f"Response: {response[:200]}")
    logger.debug(f"Tokens: input={response.usage.prompt_tokens}, output={response.usage.completion_tokens}")

    return response
```

1. **Use Langfuse for LLM observability:**

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY")
)

# Trace entire RAG pipeline
trace = langfuse.trace(name="rag_query")

# Log retrieval
retrieval = trace.span(name="retrieval")
results = await vector_store.search(query)
retrieval.end(metadata={"num_results": len(results)})

# Log LLM generation
generation = trace.generation(
    name="llm_completion",
    model="gpt-4-turbo",
    input=prompt,
    output=response
)

# View in Langfuse dashboard
```

1. **Export metrics to Prometheus:**

```python
from prometheus_client import Counter, Histogram, start_http_server

# Define metrics
llm_requests = Counter('llm_requests_total', 'Total LLM requests', ['model', 'status'])
llm_latency = Histogram('llm_latency_seconds', 'LLM request latency', ['model'])
llm_tokens = Counter('llm_tokens_total', 'Total tokens processed', ['model', 'type'])

async def complete_with_metrics(prompt: str, model: str):
    with llm_latency.labels(model=model).time():
        try:
            response = await llm.complete(prompt=prompt, model=model)
            llm_requests.labels(model=model, status='success').inc()
            llm_tokens.labels(model=model, type='input').inc(response.usage.prompt_tokens)
            llm_tokens.labels(model=model, type='output').inc(response.usage.completion_tokens)
            return response
        except Exception as e:
            llm_requests.labels(model=model, status='error').inc()
            raise

# Start Prometheus HTTP server
start_http_server(9090)
```

### Issue: Monitoring dashboard not showing data

**Symptoms:**

- Grafana dashboard is empty
- Prometheus not scraping metrics

**Solutions:**

1. **Verify Prometheus is running:**

```bash
curl http://localhost:9090/-/healthy
# Should return: Prometheus is Healthy.
```

1. **Check metrics endpoint:**

```bash
curl http://localhost:8000/metrics
# Should show Prometheus metrics
```

1. **Verify Prometheus scrape config:**

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'llm-api'
    static_configs:
      - targets: ['localhost:8000']  # Your app's metrics endpoint
```

1. **Test metric collection:**

```bash
# Check if Prometheus is collecting metrics
curl 'http://localhost:9090/api/v1/query?query=llm_requests_total'
```

---

## Getting Help

### Before Asking for Help

1. **Check this troubleshooting guide** - Most issues are covered here
2. **Review logs** - Enable debug logging and check error messages
3. **Test with simple example** - Isolate the problem
4. **Check API status** - Verify OpenAI/Anthropic/Google services are up

### Where to Get Help

**GitHub Issues (Recommended):**

- https://github.com/jeremylongshore/claude-code-plugins/issues
- Search existing issues first
- Include error logs, code snippets, and steps to reproduce

**Email Support:**

- [email protected]
- Include plugin version, Claude Code version, and detailed description

**Community Discussions:**

- GitHub Discussions: https://github.com/jeremylongshore/claude-code-plugins/discussions
- Q&A category for general questions
- #plugins channel for plugin-specific issues

### Information to Include in Support Requests

```
**Plugin Version:** ai-ml-engineering-pack v1.0.0
**Claude Code Version:** 0.1.0
**Operating System:** Ubuntu 22.04 / macOS 14.0 / Windows 11
**Python Version:** 3.11.5
**Node.js Version:** 20.10.0 (if applicable)

**Issue Description:**
[Clear description of the problem]

**Steps to Reproduce:**
1. ...
2. ...
3. ...

**Expected Behavior:**
[What should happen]

**Actual Behavior:**
[What actually happens]

**Error Logs:**
```

[Paste error logs here]

```

**Code Snippet:**
```python
# Minimal reproducible example
```

**Environment Variables:**
OPENAI_API_KEY=sk-... (redacted)
QDRANT_URL=http://localhost:6333

```

### Known Issues

Current known issues and workarounds:

1. **Qdrant Windows compatibility** - Use WSL2 or Docker for best experience
2. **Presidio slow first run** - Downloads models on first use (one-time ~500MB)
3. **Claude API rate limits** - Free tier limited to 50 requests/day

See [GitHub Issues](https://github.com/jeremylongshore/claude-code-plugins/issues) for latest updates.

---

**Still stuck?** Open a [GitHub issue](https://github.com/jeremylongshore/claude-code-plugins/issues/new) with the information template above. We typically respond within 24 hours.
