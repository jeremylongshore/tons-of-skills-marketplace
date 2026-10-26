# Domain Memory Agent

**Knowledge base with semantic search, document storage, and automatic summarization**

A lightweight MCP server for domain-specific knowledge management using TF-IDF semantic search (no external ML dependencies). Perfect for building AI memory systems and RAG applications.

## Features

- **Document Storage** - Store documents with tags and metadata
- **Semantic Search** - TF-IDF based search (no external dependencies)
- **Summarization** - Automatic extractive summaries with caching
- **Full CRUD** - Create, read, update, delete documents
- **Tagging System** - Organize knowledge by tags
- **Pagination** - Efficient browsing of large knowledge bases

## Installation

```bash
/plugin install domain-memory-agent@claude-code-plugins-plus
```

## 6 MCP Tools

### 1. `store_document`

Store documents in knowledge base with automatic indexing.

```json
{
  "title": "Machine Learning Basics",
  "content": "Machine learning is a subset of AI...",
  "tags": ["ai", "ml", "tutorial"],
  "metadata": {
    "author": "John Doe",
    "category": "Technical"
  }
}
```

### 2. `semantic_search`

Search using TF-IDF relevance scoring.

```json
{
  "query": "machine learning algorithms",
  "limit": 10,
  "offset": 0,
  "tags": ["ai"],
  "minScore": 0.1
}
```

**Returns**: Ranked results with relevance scores and excerpts, plus `totalResults`,
`showing`, `offset`, and `hasMore` for pagination.

### 3. `summarize`

Generate extractive summaries (cached).

```json
{
  "documentId": "doc123",
  "maxSentences": 5,
  "regenerate": false
}
```

### 4. `list_documents`

Browse knowledge base with filtering.

```json
{
  "tags": ["ai"],
  "sortBy": "updated",
  "limit": 50,
  "offset": 0
}
```

For `list_documents` and `semantic_search`, `limit` is an integer from 1 to 100.
Defaults remain 50 documents for listing and 10 results for search. `offset` is a
nonnegative integer and defaults to 0. Invalid paging arguments return a tool
error. Advance the offset by `showing` while `hasMore` is true, keeping the same
query, filters, and sort order. Pages reflect the current in-memory collection.

These limits count items. Document content and metadata remain intact. Search
excerpts keep their existing sentence extraction behavior and can be large;
clients retain their normal handling of large results.

### 5. `get_document`

Retrieve full document by ID.

```json
{
  "documentId": "doc123"
}
```

### 6. `delete_document`

Remove document and unindex.

```json
{
  "documentId": "doc123"
}
```

## Quick Start

```javascript
// 1. Store knowledge
store_document({
  title: "API Design Best Practices",
  content: "RESTful APIs should be...",
  tags: ["api", "architecture"]
})

// 2. Search knowledge
semantic_search({
  query: "REST API design patterns",
  limit: 5
})

// 3. Get summary
summarize({
  documentId: "doc123",
  maxSentences: 3
})
```

## How Semantic Search Works

Uses **TF-IDF** (Term Frequency-Inverse Document Frequency):

1. **Tokenization**: Text → lowercase words (filter short words)
2. **Term Frequency**: Count word occurrences in each document
3. **Document Frequency**: Track how many documents contain each term
4. **IDF**: Rare terms get higher scores
5. **TF-IDF Score**: Rank documents by relevance

**Advantages**:

- No external ML dependencies
- Fast and lightweight
- Explainable results
- Works offline

## Architecture

```
In-Memory Storage:
├── documents: Map<id, Document>
├── tfidfIndex:
│   ├── termFrequencies: Map<term, Map<docId, freq>>
│   ├── documentFrequencies: Map<term, count>
│   └── documentLengths: Map<docId, totalTerms>
```

**Note**: Data persists during session but clears on restart. Future versions will add persistence.

## Use Cases

1. **RAG Systems** - Store domain knowledge for AI retrieval
2. **Documentation Search** - Index and search project docs
3. **Research Notes** - Organize research with semantic search
4. **Customer Support** - Build knowledge bases for support agents
5. **Personal Knowledge** - Second brain / Zettelkasten system

## Performance

- **Document Storage**: < 10ms per document
- **Search**: < 50ms for 1000 documents
- **Summarization**: < 100ms per document
- **Indexing**: Real-time (synchronous)

## Best Practices

1. **Use descriptive titles** - Improves search relevance
2. **Tag consistently** - Makes filtering effective
3. **Store focused documents** - Better than huge files
4. **Cache summaries** - Regenerate only when needed
5. **Regular cleanup** - Delete outdated documents

## Example Workflows

### Building a Technical Knowledge Base

```text
# Store API documentation
store_document(title: "REST API Guide", content: "...", tags: ["api", "docs"])

# Store best practices
store_document(title: "Error Handling Patterns", content: "...", tags: ["patterns", "errors"])

# Search when needed
semantic_search(query: "handle API errors", tags: ["api"])
```

### Research Note System

```text
# Store research papers
store_document(title: "Transformer Architecture", content: "...", tags: ["ml", "nlp", "research"])

# Find related research
semantic_search(query: "attention mechanisms", tags: ["ml"])

# Get quick summary
summarize(documentId: "paper123", maxSentences: 5)
```

## License

MIT License - see [LICENSE](../../../000-docs/001-BL-LICN-license.txt)

## Related Tools

- **project-health-auditor** - Code quality analysis
- **conversational-api-debugger** - API failure debugging
- **design-to-code** - Figma to components
- **workflow-orchestrator** - Task automation

---

**Made with ️ by [Intent Solutions](https://intentsolutions.io)**
