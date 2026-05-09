# RAG (Retrieval-Augmented Generation) Pipeline - Complete Implementation Guide

## 🎯 Overview

This document explains the complete RAG pipeline implementation for the Hackostic chatbot. The system performs semantic search on traditional knowledge to generate grounded, hallucination-free responses.

## 🏗️ Architecture

### Pipeline Flow

```
User Query
    ↓
Query Embedding (Gemini API)
    ↓
Vector Similarity Search (MongoDB)
    ↓
Retrieve Top K Relevant Sources
    ↓
Context Injection into Prompt
    ↓
Gemini Response Generation
    ↓
Store Chat History + Sources
    ↓
Response to Frontend
```

## 📦 New Backend Structure

```
backend/src/ai/
├── embeddings/
│   └── embeddingService.ts          # Generates embeddings using Gemini API
├── rag/
│   ├── chunking.ts                  # Splits knowledge into semantic chunks
│   ├── retrieval.ts                 # Vector similarity search (cosine similarity)
│   └── ragChatService.ts            # Main RAG pipeline orchestration
└── prompts/
    └── ragPrompts.ts                # System prompts and context injection

backend/scripts/
└── generateEmbeddings.ts            # Batch embedding generation script
```

## 🚀 Quick Start

### 1. Install Dependencies

From the backend directory:

```bash
cd backend
npm install
```

This installs:
- `@google/genai` - Gemini API client
- `uuid` - Session ID generation

### 2. Set Environment Variables

Ensure your `.env` file has:

```env
GEMINI_API_KEY=your_gemini_api_key_here
MONGODB_URI=mongodb://127.0.0.1:27017/hackostic
```

### 3. Generate Embeddings

This is **required** before using the chat feature.

```bash
npm run generate-embeddings
```

**What it does:**
- Loads knowledge base from `data/knowledge_base/chatbot_rag_knowledge_base.json`
- Chunks long content into semantic pieces
- Generates embeddings for each chunk using Gemini API
- Stores embeddings in MongoDB `KnowledgeEmbedding` collection
- Prints statistics (total embeddings, domain breakdown)

**Expected output:**
```
🚀 Starting knowledge base embedding generation...

📡 Connecting to MongoDB...
✓ Connected to MongoDB

🗑 Clearing existing embeddings...
✓ Cleared existing embeddings

📚 Loading knowledge base...
✓ Found 142 entries

⚙ Generating embeddings (this may take a while)...

✓ [7.0%] Processed "Turmeric Milk (Haldi Doodh)" (4 chunks) - 4 embeddings stored
✓ [14.1%] Processed "Turmeric Root Powder (Haldi Powder)" (3 chunks) - 3 embeddings stored
...

✅ Embedding generation complete!

📊 Statistics:
   - Total embeddings: 512
   - Total entries: 142
   - Avg chunks per entry: 3.6

📈 Domain breakdown:
   - Home Remedies: 184 embeddings
   - Ayurveda: 98 embeddings
   - Yoga: 76 embeddings
   ...
```

### 4. Start Backend

```bash
npm run dev
```

### 5. Start Frontend

In another terminal:

```bash
cd frontend
npm run dev
```

## 🔌 API Endpoints

### POST /api/chat/query

Main RAG endpoint for chatbot queries.

**Request:**
```json
{
  "query": "What herbs help with digestion?",
  "userId": "optional_user_id",
  "sessionId": "optional_session_id_for_continuity",
  "domain": "optional_domain_filter"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "Traditional wisdom says...",
    "sources": [
      {
        "title": "Turmeric Root Powder",
        "domain": "Home Remedies",
        "similarity": 0.85
      },
      ...
    ],
    "sessionId": "session_1234567890",
    "responseTime": 2341
  }
}
```

### GET /api/chat/history/:sessionId

Retrieve chat history for a session.

**Query Parameters:**
- `limit` - Max results (default: 50, max: 200)

**Response:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "query": "What herbs help with digestion?",
        "response": "...",
        "retrievedSources": [...],
        "responseTime": 2341,
        "createdAt": "2024-05-09T10:30:00Z"
      }
    ],
    "count": 5
  }
}
```

## 🧠 How RAG Works

### 1. Query Embedding

When a user asks a question:

```typescript
const queryEmbedding = await embedQuery(userQuery)
// Returns: number[] (768-dimensional vector)
```

Uses Gemini's `text-embedding-004` model.

### 2. Vector Similarity Search

Finds semantically similar knowledge chunks:

```typescript
const results = await searchSimilarContent(queryEmbedding, {
  topK: 5,
  similarityThreshold: 0.3,
  domain: 'Home Remedies' // optional filter
})
```

**Similarity Calculation:**
```
similarity = (A · B) / (||A|| × ||B||)
// Cosine similarity between 0 and 1
```

### 3. Context Injection

Builds a prompt with retrieved context:

```
KNOWLEDGE BASE CONTEXT:
[Source 1 - Home Remedies: Turmeric Root Powder]
Turmeric contains curcumin...
Relevance Score: 85%

---

[Source 2 - Ayurveda]
In Ayurvedic medicine...
Relevance Score: 78%

---

USER QUESTION:
What herbs help with digestion?

Please provide a helpful, grounded answer...
```

### 4. Gemini Generation

AI generates response grounded in retrieved context, with system prompt:

```
You are "Wisdom Guide," a bridge between ancient and modern.
- Answer ONLY based on provided context
- Never invent cultural facts
- Use storytelling when available
- Include scientific backing
- Connect to modern relevance
```

### 5. Chat History Storage

All interactions stored in MongoDB for continuity and audit:

```typescript
{
  userId: "user_123",
  sessionId: "session_456",
  query: "What herbs help?",
  response: "...",
  retrievedSources: [...],
  modelUsed: "gemini-2.0-flash",
  responseTime: 2341,
  createdAt: ISODate(...)
}
```

## 📚 Knowledge Chunking Strategy

Long content split into **semantic chunks** with overlap:

```
Original Document (2000 words)
  ↓
Chunk 1: 500 words (0-500)
Chunk 2: 500 words (400-900)   ← 100 word overlap
Chunk 3: 500 words (800-1300)  ← 100 word overlap
Chunk 4: 700 words (1200-1900)
```

**Chunk Sizes by Content Type:**
- Remedies: 400 words
- Stories: 600 words
- Techniques: 500 words
- Historical: 550 words
- Practices: 450 words

**Breaks at:**
- Sentence boundaries (`.`, `!`, `?`)
- Paragraph boundaries (`\n`)
- Prevents mid-sentence cuts

## 🔐 Preventing Hallucinations

### Core Strategy

1. **Grounding Rule**: Prompt explicitly requires answering only from context
2. **Fallback Handling**: If no similar content found, AI suggests related topics instead of making up facts
3. **Confidence Threshold**: Results < 30% similarity discarded
4. **Error Recovery**: Failed retrievals don't break the system
5. **Audit Trail**: Sources tracked and stored for verification

### Prompt Engineering

```typescript
"Rules:
1. GROUND ALL ANSWERS IN PROVIDED CONTEXT - Non-negotiable
2. If context insufficient, say 'I don't have enough knowledge'
3. Use storytelling/scientific backing from context
4. Avoid hallucinating cultural facts
5. When appropriate, say 'I need more context about this'"
```

## 🎨 Frontend Integration

### Session Persistence

Session ID stored in localStorage:

```javascript
const getOrCreateSessionId = () => {
  let sessionId = localStorage.getItem('wisdom_guide_session')
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${randomString()}`
    localStorage.setItem('wisdom_guide_session', sessionId)
  }
  return sessionId
}
```

Enables:
- Conversation continuity across page reloads
- Conversation history retrieval
- User experience tracking

### Source Attribution

Sources displayed below AI response:

```
Sources:
• Home Remedies • Turmeric Root Powder (85%)
• Ayurveda • Digestive Herbs (78%)
```

Shows which knowledge powered the answer, building trust.

### Typing Animation

Smooth typing effect while waiting:

```jsx
{isTyping && (
  <div className="typing-indicator">
    <motion.div animate={{ y: [0, -3, 0] }} />
    <motion.div animate={{ y: [0, -3, 0] }} transition={{ delay: 0.2 }} />
    <motion.div animate={{ y: [0, -3, 0] }} transition={{ delay: 0.4 }} />
  </div>
)}
```

## 📊 Monitoring & Stats

### Retrieval Statistics

```typescript
const stats = await getRetrievalStats()
// Returns: {
//   totalEmbeddings: 512,
//   domainBreakdown: { "Home Remedies": 184, ... },
//   avgEmbeddingDimensions: 768
// }
```

### Performance Metrics

Each response includes:

```json
{
  "responseTime": 2341,  // milliseconds
  "sources": [...],      // count of retrieved
  "sessionId": "..."     // for tracking
}
```

## 🐛 Troubleshooting

### Embeddings Not Generated

**Problem:** Chat returns no sources

**Solution:**
```bash
npm run generate-embeddings
```

**Check:** Query MongoDB
```javascript
db.knowledgeembeddings.countDocuments()
// Should return > 0
```

### API Key Issues

**Error:** "Gemini API key not configured"

**Solution:**
1. Add to `.env`: `GEMINI_API_KEY=your_key`
2. Restart backend: `npm run dev`
3. Verify: API calls should work

### Rate Limiting

**Error:** "Rate limit exceeded"

**Solution:**
- Increase delay in `generateEmbeddingsBatch()` (default: 100ms)
- Use Gemini API quotas: https://ai.google.dev/docs/api_overview

### Low Similarity Scores

**Problem:** Sources rarely above threshold

**Solution:**
1. Lower threshold: `similarityThreshold: 0.2` (more permissive)
2. Increase topK: `topK: 10` (retrieve more)
3. Check embeddings quality: Are they generated?
4. Verify query is specific enough

## 🔄 Data Flow Diagram

```
┌─────────────┐
│  User Query │
└──────┬──────┘
       │
       ├─→ Query Embedding Service
       │     └─→ Gemini API
       │
       ├─→ Vector Search Service
       │     └─→ MongoDB Query
       │
       ├─→ Ranking & Filtering
       │     └─→ Cosine Similarity
       │
       ├─→ Context Building
       │     └─→ Format & Inject
       │
       ├─→ Gemini Response Gen
       │     └─→ Grounded Answer
       │
       ├─→ Chat History Storage
       │     └─→ MongoDB Save
       │
       └─→ Frontend Display
             └─→ UI Update + Sources
```

## 📈 Performance Optimization

### Caching (Future)

```typescript
// Cache popular queries
const queryCache = new Map<string, RAGChatResponse>()

// Cache similar embeddings
const embeddingCache = new Map<string, SearchResult[]>()
```

### Batch Processing (Future)

```typescript
// Process multiple queries efficiently
const batchChat = (queries: string[]) => {
  // Reuse embeddings, batch API calls
}
```

### Index Optimization (Current)

MongoDB indexes created:
```javascript
KnowledgeEmbeddingSchema.index({ domain: 1 })
KnowledgeEmbeddingSchema.index({ 'metadata.contentType': 1 })
ChatHistorySchema.index({ sessionId: 1, createdAt: -1 })
ChatHistorySchema.index({ userId: 1, createdAt: -1 })
```

## 🎓 Example Queries

### Question: "What herbs help with digestion?"

**Retrieved Sources:**
1. Turmeric Root Powder (85% similarity)
2. Ginger Treatment (78% similarity)
3. Fennel Seeds (75% similarity)

**Response Generated:**
> "Traditional wisdom recognizes several herbs for digestive health. Turmeric contains curcumin, which studies show enhances digestion by increasing bile production. Ginger is another powerful option mentioned in Ayurvedic texts—it stimulates digestive fire (agni) and reduces bloating. For best results, combine with mindful eating practices that our ancestors practiced."

**Sources Show:**
- Home Remedies • Turmeric Root Powder (85%)
- Ayurveda • Ginger Treatment (78%)
- Traditional Practices • Fennel Seeds (75%)

---

## 🚦 Next Steps

1. ✅ Generate embeddings: `npm run generate-embeddings`
2. ✅ Start backend: `npm run dev`
3. ✅ Start frontend: `npm run dev` (in frontend dir)
4. ✅ Test chatbot: Click "Ask Elder Guide"
5. ✅ Monitor: Check browser console + server logs

## 📞 Support

For issues or questions about the RAG pipeline:
1. Check server logs for API errors
2. Verify embeddings are generated
3. Test individual services
4. Review prompt engineering in `ragPrompts.ts`

---

**Last Updated:** May 9, 2026
**Version:** 1.0.0
