#!/usr/bin/env node

/**
 * Domain Memory Agent MCP Server
 *
 * Knowledge base with semantic search, document storage, and summarization.
 * Uses TF-IDF for lightweight semantic search without external ML dependencies.
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  Tool
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';
import { createHash } from 'crypto';

// ============================================================================
// Type Definitions
// ============================================================================

interface Document {
  id: string;
  title: string;
  content: string;
  metadata: Record<string, any>;
  tags: string[];
  createdAt: string;
  updatedAt: string;
  wordCount: number;
  summary?: string;
}

interface SearchResult {
  document: Document;
  score: number;
  relevantExcerpts: string[];
}

interface TFIDFIndex {
  termFrequencies: Map<string, Map<string, number>>; // term -> docId -> frequency
  documentFrequencies: Map<string, number>; // term -> number of docs containing it
  documentLengths: Map<string, number>; // docId -> total terms
  totalDocuments: number;
}

// ============================================================================
// In-Memory Storage
// ============================================================================

const documents: Map<string, Document> = new Map();
const tfidfIndex: TFIDFIndex = {
  termFrequencies: new Map(),
  documentFrequencies: new Map(),
  documentLengths: new Map(),
  totalDocuments: 0
};

// ============================================================================
// Zod Schemas
// ============================================================================

const StoreDocumentSchema = z.object({
  title: z.string().describe('Document title'),
  content: z.string().describe('Document content'),
  metadata: z.record(z.string(), z.any()).optional().default({}).describe('Additional metadata'),
  tags: z.array(z.string()).optional().default([]).describe('Tags for categorization'),
  id: z.string().optional().describe('Optional custom ID (auto-generated if not provided)')
});

const SemanticSearchSchema = z.object({
  query: z.string().describe('Search query'),
  limit: z.number().int().min(1).max(100).optional().default(10).describe('Results per page (1-100)'),
  offset: z.number().int().min(0).optional().default(0).describe('Zero-based result offset'),
  tags: z.array(z.string()).optional().describe('Filter by tags'),
  minScore: z.number().optional().default(0).describe('Minimum relevance score (0-1)')
});

const SummarizeSchema = z.object({
  documentId: z.string().optional().describe('Document ID to summarize'),
  content: z.string().optional().describe('Content to summarize directly'),
  maxSentences: z.number().optional().default(5).describe('Maximum sentences in summary'),
  regenerate: z.boolean().optional().default(false).describe('Regenerate summary even if cached')
});

const ListDocumentsSchema = z.object({
  tags: z.array(z.string()).optional().describe('Filter by tags'),
  sortBy: z.enum(['created', 'updated', 'title']).optional().default('updated'),
  limit: z.number().int().min(1).max(100).optional().default(50).describe('Documents per page (1-100)'),
  offset: z.number().int().min(0).optional().default(0).describe('Zero-based result offset')
});

const GetDocumentSchema = z.object({
  documentId: z.string().describe('Document ID to retrieve')
});

const DeleteDocumentSchema = z.object({
  documentId: z.string().describe('Document ID to delete')
});

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Generate document ID from title
 */
function generateDocumentId(title: string, customId?: string): string {
  if (customId) return customId;
  const hash = createHash('sha256').update(title + Date.now()).digest('hex');
  return hash.substring(0, 16);
}

/**
 * Tokenize text into words (lowercase, remove punctuation)
 */
function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^\w\s]/g, ' ')
    .split(/\s+/)
    .filter(word => word.length > 2); // Filter short words
}

/**
 * Calculate term frequency (TF) for a document
 */
function calculateTermFrequency(tokens: string[]): Map<string, number> {
  const tf = new Map<string, number>();
  tokens.forEach(token => {
    tf.set(token, (tf.get(token) || 0) + 1);
  });
  return tf;
}

/**
 * Update TF-IDF index with new document
 */
function indexDocument(docId: string, content: string) {
  const tokens = tokenize(content);
  const tf = calculateTermFrequency(tokens);

  // Update term frequencies for this document
  tf.forEach((freq, term) => {
    if (!tfidfIndex.termFrequencies.has(term)) {
      tfidfIndex.termFrequencies.set(term, new Map());
    }
    tfidfIndex.termFrequencies.get(term)!.set(docId, freq);
  });

  // Update document frequencies
  const uniqueTerms = new Set(tokens);
  uniqueTerms.forEach(term => {
    tfidfIndex.documentFrequencies.set(
      term,
      (tfidfIndex.documentFrequencies.get(term) || 0) + 1
    );
  });

  // Store document length
  tfidfIndex.documentLengths.set(docId, tokens.length);
  tfidfIndex.totalDocuments++;
}

/**
 * Remove document from TF-IDF index
 */
function unindexDocument(docId: string) {
  const terms = Array.from(tfidfIndex.termFrequencies.keys());

  terms.forEach(term => {
    const docFreqs = tfidfIndex.termFrequencies.get(term);
    if (docFreqs?.has(docId)) {
      docFreqs.delete(docId);

      // Update document frequency
      const currentDF = tfidfIndex.documentFrequencies.get(term) || 0;
      tfidfIndex.documentFrequencies.set(term, Math.max(0, currentDF - 1));

      // Remove term if no documents contain it
      if (docFreqs.size === 0) {
        tfidfIndex.termFrequencies.delete(term);
        tfidfIndex.documentFrequencies.delete(term);
      }
    }
  });

  tfidfIndex.documentLengths.delete(docId);
  tfidfIndex.totalDocuments = Math.max(0, tfidfIndex.totalDocuments - 1);
}

/**
 * Calculate TF-IDF score for a query against a document
 */
function calculateTFIDF(queryTokens: string[], docId: string): number {
  let score = 0;
  const docLength = tfidfIndex.documentLengths.get(docId) || 1;

  queryTokens.forEach(term => {
    const termFreqMap = tfidfIndex.termFrequencies.get(term);
    if (!termFreqMap) return;

    const tf = (termFreqMap.get(docId) || 0) / docLength;
    const df = tfidfIndex.documentFrequencies.get(term) || 0;
    const idf = df > 0 ? Math.log((tfidfIndex.totalDocuments + 1) / (df + 1)) : 0;

    score += tf * idf;
  });

  return score;
}

/**
 * Extract relevant excerpts from document for query
 */
function extractRelevantExcerpts(
  content: string,
  queryTokens: string[],
  maxExcerpts: number = 3
): string[] {
  const sentences = content
    .split(/[.!?]+/)
    .map(s => s.trim())
    .filter(s => s.length > 20);

  // Score each sentence by query term presence
  const scoredSentences = sentences.map(sentence => {
    const sentenceTokens = new Set(tokenize(sentence));
    const matchCount = queryTokens.filter(token => sentenceTokens.has(token)).length;
    return { sentence, score: matchCount };
  });

  // Return top scoring sentences
  return scoredSentences
    .sort((a, b) => b.score - a.score)
    .slice(0, maxExcerpts)
    .map(s => s.sentence)
    .filter(s => s.length > 0);
}

/**
 * Generate extractive summary (key sentences)
 */
function generateSummary(content: string, maxSentences: number = 5): string {
  const sentences = content
    .split(/[.!?]+/)
    .map(s => s.trim())
    .filter(s => s.length > 20);

  if (sentences.length <= maxSentences) {
    return sentences.join('. ') + '.';
  }

  // Score sentences by term frequency and position
  const tokens = tokenize(content);
  const termFreq = calculateTermFrequency(tokens);

  const scoredSentences = sentences.map((sentence, index) => {
    const sentenceTokens = tokenize(sentence);

    // Score based on important terms
    let score = sentenceTokens.reduce((sum, token) => {
      return sum + (termFreq.get(token) || 0);
    }, 0);

    // Boost first and last sentences slightly
    if (index === 0 || index === sentences.length - 1) {
      score *= 1.2;
    }

    return { sentence, score, index };
  });

  // Select top sentences, maintain order
  const topSentences = scoredSentences
    .sort((a, b) => b.score - a.score)
    .slice(0, maxSentences)
    .sort((a, b) => a.index - b.index)
    .map(s => s.sentence);

  return topSentences.join('. ') + '.';
}

// ============================================================================
// Document Operations
// ============================================================================

/**
 * Store a document in the knowledge base
 */
async function storeDocument(args: z.infer<typeof StoreDocumentSchema>) {
  const { title, content, metadata, tags, id: customId } = args;

  const docId = generateDocumentId(title, customId);
  const now = new Date().toISOString();
  const wordCount = content.split(/\s+/).length;

  // If document exists, unindex old version first
  if (documents.has(docId)) {
    unindexDocument(docId);
  }

  const document: Document = {
    id: docId,
    title,
    content,
    metadata,
    tags,
    createdAt: documents.get(docId)?.createdAt || now,
    updatedAt: now,
    wordCount
  };

  // Store document
  documents.set(docId, document);

  // Index for search
  indexDocument(docId, `${title} ${content}`);

  return {
    id: docId,
    title,
    wordCount,
    tags,
    createdAt: document.createdAt,
    updatedAt: document.updatedAt,
    stored: true
  };
}

/**
 * Search documents using TF-IDF semantic search
 */
async function semanticSearch(args: z.infer<typeof SemanticSearchSchema>) {
  const { query, limit, offset, tags: filterTags, minScore } = args;

  const queryTokens = tokenize(query);
  if (queryTokens.length === 0) {
    return { results: [], totalResults: 0, query, showing: 0, offset, hasMore: false };
  }

  // Calculate scores for all documents
  const results: SearchResult[] = [];

  for (const [docId, doc] of documents.entries()) {
    // Filter by tags if specified
    if (filterTags && filterTags.length > 0) {
      const hasMatchingTag = doc.tags.some(tag => filterTags.includes(tag));
      if (!hasMatchingTag) continue;
    }

    const score = calculateTFIDF(queryTokens, docId);

    if (score >= minScore) {
      const excerpts = extractRelevantExcerpts(doc.content, queryTokens);
      results.push({
        document: doc,
        score,
        relevantExcerpts: excerpts
      });
    }
  }

  // Sort by score descending
  results.sort((a, b) => b.score - a.score);

  // Limit results
  const limitedResults = results.slice(offset, offset + limit);

  return {
    results: limitedResults.map(r => ({
      id: r.document.id,
      title: r.document.title,
      score: Math.round(r.score * 1000) / 1000,
      relevantExcerpts: r.relevantExcerpts,
      tags: r.document.tags,
      wordCount: r.document.wordCount,
      updatedAt: r.document.updatedAt
    })),
    totalResults: results.length,
    query,
    showing: limitedResults.length,
    offset,
    hasMore: offset + limitedResults.length < results.length
  };
}

/**
 * Summarize a document or content
 */
async function summarize(args: z.infer<typeof SummarizeSchema>) {
  const { documentId, content: directContent, maxSentences, regenerate } = args;

  let content: string;
  let docId: string | undefined;

  if (documentId) {
    const doc = documents.get(documentId);
    if (!doc) {
      throw new Error(`Document not found: ${documentId}`);
    }

    // Return cached summary if available and not regenerating
    if (doc.summary && !regenerate) {
      return {
        summary: doc.summary,
        cached: true,
        documentId,
        sentenceCount: doc.summary.split(/[.!?]+/).length - 1
      };
    }

    content = doc.content;
    docId = documentId;
  } else if (directContent) {
    content = directContent;
  } else {
    throw new Error('Either documentId or content must be provided');
  }

  // Generate summary
  const summary = generateSummary(content, maxSentences);
  const sentenceCount = summary.split(/[.!?]+/).length - 1;

  // Cache summary if document ID provided
  if (docId) {
    const doc = documents.get(docId);
    if (doc) {
      doc.summary = summary;
      doc.updatedAt = new Date().toISOString();
    }
  }

  return {
    summary,
    cached: false,
    documentId: docId,
    sentenceCount,
    originalLength: content.split(/\s+/).length,
    summaryLength: summary.split(/\s+/).length
  };
}

/**
 * List documents in knowledge base
 */
async function listDocuments(args: z.infer<typeof ListDocumentsSchema>) {
  const { tags: filterTags, sortBy, limit, offset } = args;

  let docs = Array.from(documents.values());

  // Filter by tags
  if (filterTags && filterTags.length > 0) {
    docs = docs.filter(doc =>
      doc.tags.some(tag => filterTags.includes(tag))
    );
  }

  // Sort
  docs.sort((a, b) => {
    switch (sortBy) {
      case 'created':
        return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
      case 'updated':
        return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
      case 'title':
        return a.title.localeCompare(b.title);
      default:
        return 0;
    }
  });

  // Paginate
  const paginatedDocs = docs.slice(offset, offset + limit);

  return {
    documents: paginatedDocs.map(doc => ({
      id: doc.id,
      title: doc.title,
      tags: doc.tags,
      wordCount: doc.wordCount,
      hasSummary: !!doc.summary,
      createdAt: doc.createdAt,
      updatedAt: doc.updatedAt,
      metadata: doc.metadata
    })),
    total: docs.length,
    showing: paginatedDocs.length,
    offset,
    hasMore: offset + limit < docs.length
  };
}

/**
 * Get a specific document
 */
async function getDocument(args: z.infer<typeof GetDocumentSchema>) {
  const { documentId } = args;

  const doc = documents.get(documentId);
  if (!doc) {
    throw new Error(`Document not found: ${documentId}`);
  }

  return {
    id: doc.id,
    title: doc.title,
    content: doc.content,
    tags: doc.tags,
    wordCount: doc.wordCount,
    summary: doc.summary,
    metadata: doc.metadata,
    createdAt: doc.createdAt,
    updatedAt: doc.updatedAt
  };
}

/**
 * Delete a document
 */
async function deleteDocument(args: z.infer<typeof DeleteDocumentSchema>) {
  const { documentId } = args;

  const doc = documents.get(documentId);
  if (!doc) {
    throw new Error(`Document not found: ${documentId}`);
  }

  // Remove from index
  unindexDocument(documentId);

  // Delete document
  documents.delete(documentId);

  return {
    deleted: true,
    documentId,
    title: doc.title
  };
}

// ============================================================================
// MCP Server Setup
// ============================================================================

const server = new Server(
  {
    name: 'knowledge-base',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Define available tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const tools: Tool[] = [
    {
      name: 'store_document',
      description: 'Store a document in the knowledge base with optional tags and metadata. Content is automatically indexed for semantic search.',
      inputSchema: z.toJSONSchema(StoreDocumentSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema']
    },
    {
      name: 'semantic_search',
      description: 'Search documents using TF-IDF semantic search. Returns relevant documents with excerpts and relevance scores.',
      inputSchema: z.toJSONSchema(SemanticSearchSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema']
    },
    {
      name: 'summarize',
      description: 'Generate extractive summary of a document or content. Summaries are cached for documents.',
      inputSchema: z.toJSONSchema(SummarizeSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema']
    },
    {
      name: 'list_documents',
      description: 'List all documents in knowledge base with filtering, sorting, and pagination.',
      inputSchema: z.toJSONSchema(ListDocumentsSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema']
    },
    {
      name: 'get_document',
      description: 'Retrieve a specific document by ID including full content.',
      inputSchema: z.toJSONSchema(GetDocumentSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema']
    },
    {
      name: 'delete_document',
      description: 'Delete a document from the knowledge base and remove from search index.',
      inputSchema: z.toJSONSchema(DeleteDocumentSchema, { target: 'draft-07', io: 'input' }) as Tool['inputSchema']
    }
  ];

  return { tools };
});

// Handle tool execution
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    if (name === 'store_document') {
      const validatedArgs = StoreDocumentSchema.parse(args);
      const result = await storeDocument(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    if (name === 'semantic_search') {
      const validatedArgs = SemanticSearchSchema.parse(args);
      const result = await semanticSearch(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    if (name === 'summarize') {
      const validatedArgs = SummarizeSchema.parse(args);
      const result = await summarize(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    if (name === 'list_documents') {
      const validatedArgs = ListDocumentsSchema.parse(args);
      const result = await listDocuments(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    if (name === 'get_document') {
      const validatedArgs = GetDocumentSchema.parse(args);
      const result = await getDocument(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    if (name === 'delete_document') {
      const validatedArgs = DeleteDocumentSchema.parse(args);
      const result = await deleteDocument(validatedArgs);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }]
      };
    }

    throw new Error(`Unknown tool: ${name}`);
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({ error: errorMessage }, null, 2)
      }],
      isError: true
    };
  }
});

// Start the server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('Knowledge Base MCP server running on stdio');
}

main().catch((error) => {
  console.error('Fatal error in main():', error);
  process.exit(1);
});
