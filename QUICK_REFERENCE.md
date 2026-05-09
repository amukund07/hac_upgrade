# RAG Pipeline - Quick Reference

## 🎯 Quick Start

```bash
# 1. Install dependencies
cd backend && npm install

# 2. Generate embeddings (CRITICAL!)
npm run generate-embeddings

# 3. Start backend
npm run dev

# 4. In another terminal, start frontend
cd frontend && npm run dev

# 5. Open http://localhost:5173
# Click "Ask Elder Guide" button
# Ask a question!
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `backend/src/ai/embeddings/embeddingService.ts` | Generate embeddings |
| `backend/src/ai/rag/chunking.ts` | Split documents into chunks |
| `backend/src/ai/rag/retrieval.ts` | Vector similarity search |
| `backend/src/ai/rag/ragChatService.ts` | Main RAG pipeline |
| `backend/src/ai/prompts/ragPrompts.ts` | Prompt engineering |
| `backend/scripts/generateEmbeddings.ts` | Batch processing script |
| `frontend/src/components/chat/ChatPopup.tsx` | Chat UI |

## 🚀 API Endpoints

### POST /api/chat/query

Send a message and get a RAG response.

```javascript
// Request
fetch('http://localhost:5000/api/chat/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "What herbs help with digestion?",
    sessionId: "session_123", // optional
    userId: "user_456"        // optional
  })
})

// Response
{
  "success": true,
  "data": {
    "response": "Turmeric, ginger, and fennel are...",
    "sources": [
      { "title": "Turmeric Milk", "domain": "Home Remedies", "similarity": 0.85 }
    ],
    "sessionId": "session_123",
    "responseTime": 2341
  }
}
```

### GET /api/chat/history/:sessionId

Get chat history.

```javascript
// Request
fetch('http://localhost:5000/api/chat/history/session_123?limit=10')

// Response
{
  "success": true,
  "data": {
    "history": [...],
    "count": 5
  }
}
```

## 🔧 Configuration

### Environment Variables

```env
GEMINI_API_KEY=your_key_here
MONGODB_URI=mongodb://127.0.0.1:27017/hackostic
```

### Code Configuration

```typescript
// In chatController.ts
const response = await generateRAGChatResponse(query, {
  topK: 5,                    // Number of sources to retrieve
  similarityThreshold: 0.3,   // Minimum similarity (0-1)
  domain: 'Home Remedies'     // Optional filter
})
```

## 🔍 Debugging

### Enable Logging

```typescript
// In ragChatService.ts, logs show:
console.log('[RAG] Generating query embedding...')
console.log('[RAG] Searching for similar content...')
console.log('[RAG] Found 5 relevant sources, generating answer...')
console.log('[RAG] Calling Gemini API...')
```

### Check Embeddings

```javascript
// MongoDB
use hackostic
db.knowledgeembeddings.countDocuments()
// Should return > 0

// Check specific domain
db.knowledgeembeddings.countDocuments({ domain: "Home Remedies" })
```

### Monitor Response

```javascript
// Browser DevTools → Network → Find /chat/query request
// Response should include:
{
  "data": {
    "response": "...",
    "sources": [...],  // ← Should not be empty
    "responseTime": 2341
  }
}
```

## 🎯 Common Tasks

### Add New Knowledge

1. Edit `data/knowledge_base/chatbot_rag_knowledge_base.json`
2. Add entry with title, domain, content, etc.
3. Regenerate embeddings: `npm run generate-embeddings`

### Customize AI Personality

Edit `backend/src/ai/prompts/ragPrompts.ts`:

```typescript
export const RAG_SYSTEM_PROMPT = `
  You are "Wisdom Guide," a bridge between ancient...
  
  // Modify these instructions to change AI behavior
  Rules:
  1. GROUND ALL ANSWERS IN PROVIDED CONTEXT
  2. If context insufficient, say "I don't have..."
  3. Use storytelling when available
  ...
`
```

### Adjust Retrieval Sensitivity

In `backend/src/controllers/chatController.ts`:

```typescript
// More lenient (lower threshold = more results)
similarityThreshold: 0.2  // Default: 0.3

// More strict (higher threshold = better matches)
similarityThreshold: 0.5  // Default: 0.3

// Get more sources
topK: 10  // Default: 5
```

### Filter by Domain

```typescript
// In chat request
await generateRAGChatResponse(query, {
  domain: 'Home Remedies'  // Only search this domain
})
```

## ⚡ Performance Tips

### 1. Batch Processing (Future)

```typescript
// Process multiple queries together
const queries = [
  "What is yoga?",
  "How to meditate?",
  "Benefits of ayurveda?"
]

// Combine embeddings to reduce API calls
```

### 2. Caching (Future)

```typescript
// Cache query embeddings
const cache = new Map<string, number[]>()

// Check cache before API call
if (cache.has(query)) {
  return cache.get(query)  // 10ms vs 800ms
}
```

### 3. MongoDB Indexing

Indexes already created:
```
db.knowledgeembeddings.createIndex({ domain: 1 })
db.knowledgeembeddings.createIndex({ "metadata.contentType": 1 })
db.chathistory.createIndex({ sessionId: 1, createdAt: -1 })
```

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Gemini API key not configured" | Add `GEMINI_API_KEY` to `.env` |
| No sources shown | Run `npm run generate-embeddings` |
| Slow responses | Check internet, Gemini quota |
| MongoDB connection error | Ensure MongoDB is running |
| Empty responses | Check embeddings exist in DB |

## 📊 Typical Response Times

| Step | Time |
|------|------|
| Query embedding | 800ms |
| Database search | 150ms |
| Prompt building | 50ms |
| Gemini generation | 1200ms |
| History storage | 100ms |
| **Total** | **~2300ms** |

## 🎓 Example Queries

```
"What is turmeric good for?"
"Tell me a folk story about courage"
"How to practice yoga for flexibility?"
"What herbs help with sleep?"
"Explain Vedic mathematics"
"Benefits of sustainable farming"
"Traditional martial arts techniques"
```

## 📚 Documentation

- **Full Setup**: [SETUP_RAG.md](./SETUP_RAG.md)
- **Architecture**: [RAG_ARCHITECTURE.md](./RAG_ARCHITECTURE.md)
- **Implementation**: [RAG_IMPLEMENTATION_GUIDE.md](./RAG_IMPLEMENTATION_GUIDE.md)

## 🔗 Links

- Gemini API Docs: https://ai.google.dev/docs
- MongoDB Docs: https://docs.mongodb.com
- Vector Search: https://en.wikipedia.org/wiki/Cosine_similarity

## 💡 Pro Tips

1. **Session Persistence**: Session ID stored in localStorage - users see chat history
2. **Source Attribution**: Display sources below each response - builds trust
3. **Typing Animation**: Shows while processing - better UX
4. **Auto-play Audio**: Responses play automatically - more accessible
5. **Error Graceful**: System never crashes - falls back gracefully

## 🚦 Development Workflow

```
1. Make code changes
2. Backend auto-reloads (npm run dev)
3. Frontend auto-reloads (npm run dev)
4. Test in browser
5. Check browser console for errors
6. Check backend logs for [RAG] messages
7. Verify MongoDB stores chat history
```

---

**Need Help?**
- Check logs: Look for `[RAG]` messages in backend console
- Debug: Enable browser DevTools Network tab
- Test: Use curl or Postman to test API directly
- Reference: See full docs in RAG_*.md files

**Last Updated:** May 9, 2026
