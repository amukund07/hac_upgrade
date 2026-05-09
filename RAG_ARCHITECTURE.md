# RAG Architecture & Design Decisions

## 📐 System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                            │
│  React/TypeScript │ ChatPopup Component │ Session Management    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    HTTP REST API Calls
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Layer                          │
│  Express.js │ Routes │ Controllers │ Request Validation         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    RAG Processing Pipeline                      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Step 1: Query Embedding                                │   │
│  │ Input: User question                                    │   │
│  │ Service: embeddingService.ts                           │   │
│  │ API: Gemini text-embedding-004                         │   │
│  │ Output: 768-dimensional vector                         │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Step 2: Vector Similarity Search                        │   │
│  │ Input: Query embedding                                  │   │
│  │ Service: retrieval.ts                                  │   │
│  │ Database: MongoDB KnowledgeEmbedding collection        │   │
│  │ Algorithm: Cosine similarity                           │   │
│  │ Output: Top K relevant chunks with scores              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Step 3: Context Injection                               │   │
│  │ Input: User query + retrieved sources                   │   │
│  │ Service: ragPrompts.ts                                 │   │
│  │ Process: Format context + build prompt                  │   │
│  │ Output: System prompt + user prompt                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Step 4: Gemini Response Generation                      │   │
│  │ Input: System prompt + user prompt with context         │   │
│  │ API: Gemini 2.0 Flash                                  │   │
│  │ Process: Generate grounded response                     │   │
│  │ Output: AI-generated answer                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Step 5: History & Analytics                             │   │
│  │ Store: Query, response, sources, metadata               │   │
│  │ Database: MongoDB ChatHistory collection                │   │
│  │ Purpose: Continuity, audit, analytics                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Data Storage Layer                            │
│  MongoDB Collections:                                           │
│  - KnowledgeEmbedding: {embedding[], domain, content}          │
│  - ChatHistory: {query, response, sources, sessionId}          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                   External APIs                                 │
│  - Gemini API: Embeddings + Generation                         │
│  - MongoDB Atlas: Data persistence                              │
└─────────────────────────────────────────────────────────────────┘
```

## 🗂️ File Structure & Responsibilities

### Backend Services

#### `backend/src/ai/embeddings/embeddingService.ts`
- **Purpose**: Generate vector embeddings for text
- **Key Functions**:
  - `generateEmbedding(text)` - Single embedding via Gemini API
  - `generateEmbeddingsBatch(texts)` - Multiple embeddings with rate limiting
  - `embedQuery(query)` - Optimize query embedding generation
- **Dependencies**: GoogleGenAI client
- **Performance**: ~5-10 requests/minute with delays to avoid rate limiting

#### `backend/src/ai/rag/chunking.ts`
- **Purpose**: Split long documents into manageable chunks
- **Key Functions**:
  - `chunkText(text)` - Split at sentence boundaries
  - `chunkKnowledgeEntry(entry)` - Process knowledge base entries
  - `getOptimalChunkSize(contentType)` - Adaptive sizing
- **Strategy**:
  - Preserves semantic meaning
  - 20% overlap between chunks
  - Breaks at natural boundaries (sentences, paragraphs)
- **Chunk Sizes**:
  - Remedies: 400 words
  - Stories: 600 words
  - Techniques: 500 words

#### `backend/src/ai/rag/retrieval.ts`
- **Purpose**: Perform semantic search on embedded knowledge
- **Key Functions**:
  - `cosineSimilarity(vecA, vecB)` - Calculate vector similarity
  - `searchSimilarContent(embedding, options)` - Main search function
  - `formatRetrievedSources(results)` - Format for chat history
  - `getRetrievalStats()` - Analytics
- **Similarity Algorithm**: Cosine similarity (0 to 1 scale)
- **Filtering**: Domain, content type, similarity threshold
- **Ranking**: Sort by similarity descending, return top K

#### `backend/src/ai/prompts/ragPrompts.ts`
- **Purpose**: Engineer prompts for grounded AI responses
- **Key Functions**:
  - `RAG_SYSTEM_PROMPT` - Core instructions for AI
  - `buildKnowledgeContext(sources)` - Format retrieved knowledge
  - `buildRAGPrompt(query, context)` - Combine user query with context
  - `buildFallbackPrompt(query)` - Handle missing context gracefully
- **Hallucination Prevention**:
  - Explicit grounding rules
  - "Say when you don't know" instructions
  - Context-only answers requirement

#### `backend/src/ai/rag/ragChatService.ts`
- **Purpose**: Orchestrate complete RAG pipeline
- **Key Functions**:
  - `generateRAGChatResponse(query, options)` - Main pipeline
  - `getChatHistory(sessionId)` - Retrieve past conversations
  - `getUserChatSessions(userId)` - Get user's sessions
  - `clearChatHistory(sessionId)` - Cleanup
- **Error Handling**: Graceful degradation with fallback responses
- **Session Management**: Track conversations for continuity
- **Metrics**: Response time, source count, session tracking

### Controllers & Routes

#### `backend/src/controllers/chatController.ts`
- **Updated for RAG**:
  - `chat()` - Accepts `query`, `sessionId`, `userId`, `domain`
  - `getChatHistoryHandler()` - Retrieve history with pagination
- **Validation**: Check query is non-empty string
- **Response Format**: Includes sources, response time, session ID

#### `backend/src/routes/chatRoutes.ts`
- **Endpoints**:
  - `POST /api/chat/query` - Send message, get RAG response
  - `GET /api/chat/history/:sessionId` - Get conversation history

### Scripts

#### `backend/scripts/generateEmbeddings.ts`
- **Purpose**: Batch process knowledge base into embeddings
- **Process**:
  1. Load JSON knowledge base
  2. Chunk each entry
  3. Generate embeddings via API
  4. Store in MongoDB
  5. Report statistics
- **Features**:
  - Progress tracking
  - Error recovery
  - Rate limiting
  - Domain breakdown stats
- **Runtime**: 5-15 minutes depending on knowledge base size

## 🔄 Data Flow Diagrams

### User Query Processing

```
User Message
    ↓
[ChatPopup Component]
- Validates input
- Shows typing animation
- Generates session ID
    ↓
POST /api/chat/query
    ↓
[Chat Controller]
- Validates request
- Passes to service
    ↓
[RAG Chat Service]
    ├─→ embedQuery()
    │   └─→ Gemini API
    │
    ├─→ searchSimilarContent()
    │   └─→ MongoDB Query
    │       └─→ Cosine Similarity
    │
    ├─→ buildPrompt()
    │   └─→ Context Injection
    │
    ├─→ generateGeminiResponse()
    │   └─→ Gemini API
    │
    ├─→ storeChatHistory()
    │   └─→ MongoDB Save
    │
    └─→ Return Response
        ├─→ response: string
        ├─→ sources: []
        ├─→ sessionId: string
        └─→ responseTime: number
    ↓
[Chat Controller]
- Formats response
- Sends JSON
    ↓
HTTP Response
    ↓
[ChatPopup Component]
- Stops typing animation
- Displays response
- Shows sources
- Plays audio
```

### Embedding Generation Pipeline

```
Knowledge Base JSON
(data/knowledge_base/*.json)
    ↓
[generateEmbeddings.ts]
    ├─→ Load JSON files
    │
    ├─→ For each entry:
    │   ├─→ chunkKnowledgeEntry()
    │   │   └─→ Split into chunks
    │   │
    │   ├─→ generateEmbeddingsBatch()
    │   │   └─→ For each chunk:
    │   │       └─→ Gemini API
    │   │
    │   └─→ KnowledgeEmbedding.insertMany()
    │       └─→ Store in MongoDB
    │
    ├─→ Progress tracking
    │
    └─→ Stats reporting
        ├─→ Total embeddings
        ├─→ Domain breakdown
        └─→ Avg chunks per entry
```

## 🎯 Design Decisions

### 1. Chunking Strategy

**Why Chunks?**
- Embeddings work better with focused content (~500 words)
- Allows fine-grained retrieval
- Prevents context overload

**Why Overlap?**
- Maintains semantic continuity
- Ensures important concepts aren't split
- Improves retrieval accuracy

**Why Semantic Boundaries?**
- Breaks at `.`, `!`, `?` instead of arbitrary positions
- Preserves meaning
- Better for AI comprehension

### 2. Cosine Similarity

**Why Cosine Similarity?**
- Standard for semantic search
- Efficient computation
- Scale-invariant (0 to 1)
- Works well with embeddings

**Formula:**
```
similarity = (A · B) / (||A|| × ||B||)
```

### 3. Multi-Step Prompt Engineering

**Why System + User Prompts?**
- Separates instructions from query
- More control over AI behavior
- Better for instruction following
- Easier to test/modify

**System Prompt includes:**
- Role definition ("Wisdom Guide")
- Core rules (ground in context)
- Tone guidelines
- Error handling instructions

**User Prompt includes:**
- Retrieved context sections
- User question
- Session context if applicable

### 4. Session-Based Architecture

**Benefits:**
- Conversation continuity
- User analytics
- Audit trail
- Better UX (remember previous messages)

**Implementation:**
- localStorage for frontend session ID
- MongoDB index on sessionId
- Enables history retrieval

### 5. Error Graceful Degradation

**Fallback Strategy:**
1. Try RAG with retrieved context
2. If retrieval fails, use fallback prompt
3. If generation fails, use fallback response
4. Never crash, always respond

**Benefits:**
- Robust system
- Better UX
- Visible error handling

## 🔐 Hallucination Prevention Architecture

### Layer 1: Data Layer
- Only store verified knowledge
- Sources tracked and auditable
- Domain-specific categorization

### Layer 2: Retrieval Layer
- Similarity threshold filtering
- Return ranked sources
- Empty retrieval detection

### Layer 3: Prompt Layer
- Explicit grounding requirement
- "Say when you don't know" instruction
- Prohibit invention of facts

### Layer 4: API Layer
- Validate response completeness
- Log sources with response
- Track confidence metrics

### Layer 5: UI Layer
- Display sources prominently
- Show similarity scores
- Build user trust

## 📊 Performance Characteristics

### Latency Breakdown (Typical)

```
User Query
    ├─→ Generate embedding: 800ms
    ├─→ Search DB: 150ms
    ├─→ Build context: 50ms
    ├─→ Gemini generation: 1200ms
    ├─→ Store history: 100ms
    └─→ Total: ~2300ms (2.3 seconds)

User sees: Typing animation 1000-2000ms
```

### Throughput

- Sequential: 25 requests/minute
- With caching: 100+ requests/minute (future)
- Bottleneck: Gemini API rate limits

### Storage

- Average embeddings per entry: 3-4
- Vector dimensions: 768 (384KB per embedding)
- Knowledge base: 142 entries → ~512 embeddings → ~200MB total
- Chat history: ~1KB per conversation

## 🔄 Scaling Considerations

### Horizontal Scaling

```
Load Balancer
    ├─→ Backend Instance 1
    ├─→ Backend Instance 2
    └─→ Backend Instance N
        ↓
    MongoDB (shared)
        ↓
    Embeddings Cache (Redis future)
```

### Embedding Cache

```typescript
// Cache query embeddings
const queryCache = new Map<string, number[]>()

// Check cache before generating
if (queryCache.has(query)) {
  return queryCache.get(query)
}

// Generate and cache
const embedding = await generateEmbedding(query)
queryCache.set(query, embedding)
```

### Batch Processing

```typescript
// Process multiple queries together
const batchChat = async (queries: string[]) => {
  // Deduplicate embeddings
  // Batch MongoDB queries
  // Batch API calls
}
```

## 🧪 Testing Strategy

### Unit Tests

```typescript
// embeddingService
- generateEmbedding returns 768-d vector
- generateEmbeddingsBatch handles errors
- embedQuery formats correctly

// retrieval
- cosineSimilarity calculation correct
- searchSimilarContent filters properly
- formatRetrievedSources formats output

// chunking
- chunkText breaks at boundaries
- chunkKnowledgeEntry combines fields
- getOptimalChunkSize returns correct size
```

### Integration Tests

```typescript
// Full RAG pipeline
- Query → Embeddings → Search → Response
- Chat history properly stored
- Sources correctly attributed
- Error cases handled gracefully
```

### Performance Tests

```typescript
// Benchmark
- Embedding generation time
- Database query latency
- Full request round-trip time
- Concurrent user load
```

## 📈 Monitoring & Observability

### Metrics to Track

```
Per Request:
- query_embedding_time
- search_latency
- gemini_generation_time
- total_response_time
- sources_retrieved
- similarity_scores

Per Session:
- messages_count
- avg_response_time
- domains_accessed

Per System:
- total_embeddings
- cache_hit_rate
- error_rate
- api_quota_usage
```

### Logging

```
[RAG] Generating query embedding...
[RAG] Searching for similar content...
[RAG] Found 5 relevant sources, generating answer...
[RAG] Calling Gemini API...
[RAG] Response generated in 2341ms
```

### Error Tracking

```
[ERROR] Gemini API failed: rate_limit_exceeded
[ERROR] MongoDB connection timeout
[ERROR] Empty embedding returned
[ERROR] No similar content found (fallback)
```

## 🔮 Future Enhancements

### 1. Advanced Caching

```typescript
- Query embedding cache (Redis)
- Frequent query pre-computed
- Popular topics pre-ranked
```

### 2. Semantic Routers

```typescript
- Route to specialized models
- Domain-specific fine-tuning
- Multi-stage retrieval
```

### 3. Re-ranking

```typescript
- Second-stage ranking
- Combine multiple signals
- Learn from user feedback
```

### 4. Feedback Loop

```typescript
- Track which sources were helpful
- Re-rank based on usage
- Continuous improvement
```

### 5. Knowledge Updates

```typescript
- Incremental embedding updates
- Change detection
- Batch refresh strategy
```

## 📚 References

### Papers
- "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks" (Lewis et al., 2020)
- "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks" (Reimers & Gurevych, 2019)

### APIs
- Gemini API: https://ai.google.dev/docs
- MongoDB: https://docs.mongodb.com
- Cosine Similarity: https://en.wikipedia.org/wiki/Cosine_similarity

---

**Last Updated:** May 9, 2026
