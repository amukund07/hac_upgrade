# 🚀 RAG Pipeline Setup Instructions

Complete step-by-step guide to get the RAG chatbot working.

## Prerequisites

✅ Node.js 16+ installed  
✅ MongoDB running locally or connection string ready  
✅ Gemini API key (get from https://ai.google.dev)  
✅ Project already has frontend and backend set up  

## Step 1: Backend Setup

### 1.1 Navigate to Backend

```bash
cd backend
```

### 1.2 Install Dependencies

```bash
npm install
```

This adds:
- `@google/genai` - Gemini API integration
- `uuid` - For session ID generation

### 1.3 Configure Environment Variables

Create or update `backend/.env`:

```env
# MongoDB
MONGODB_URI=mongodb://127.0.0.1:27017/hackostic

# Gemini API
GEMINI_API_KEY=your_actual_gemini_api_key_here

# Server
PORT=5000
CLIENT_ORIGIN=http://localhost:5173

# JWT
JWT_SECRET=your_secret_key_here
JWT_EXPIRES_IN=7d
```

**Getting Gemini API Key:**
1. Go to https://ai.google.dev/
2. Click "Get API Key"
3. Create new API key in Google Cloud Console
4. Copy and paste into `.env`

### 1.4 Verify MongoDB Connection

```bash
# Test connection (optional)
node -e "require('mongoose').connect('mongodb://127.0.0.1:27017/hackostic').then(() => console.log('✓ MongoDB connected')).catch(e => console.error('✗ Connection failed:', e.message))"
```

## Step 2: Generate Embeddings (CRITICAL)

This must be done before using the chat feature.

### 2.1 Run Embedding Generation

```bash
npm run generate-embeddings
```

### 2.2 Wait for Completion

Expected time: 5-15 minutes depending on knowledge base size

**Output will show:**
```
🚀 Starting knowledge base embedding generation...
📡 Connecting to MongoDB...
✓ Connected to MongoDB

🗑 Clearing existing embeddings...
✓ Cleared existing embeddings

📚 Loading knowledge base...
✓ Found 142 entries

⚙ Generating embeddings (this may take a while)...

✓ [0.7%] Processed "Turmeric Milk" (4 chunks) - 4 embeddings stored
✓ [1.4%] Processed "Golden Milk Recipe" (3 chunks) - 3 embeddings stored
...
✓ [100.0%] Processed "Last Entry" (5 chunks) - 5 embeddings stored

✅ Embedding generation complete!

📊 Statistics:
   - Total embeddings: 512
   - Total entries: 142
   - Avg chunks per entry: 3.6

📈 Domain breakdown:
   - Home Remedies: 184 embeddings
   - Ayurveda: 98 embeddings
   - Yoga: 76 embeddings
   - ...
```

### 2.3 Verify Embeddings Generated

Check MongoDB:

```bash
node -e "require('mongoose').connect('mongodb://127.0.0.1:27017/hackostic').then(async () => { const count = await require('mongoose').connection.collection('knowledgeembeddings').countDocuments(); console.log('Embeddings in DB:', count); process.exit(0); })"
```

Should show: `Embeddings in DB: 500+`

## Step 3: Build Backend

```bash
npm run build
```

Creates `dist/` folder with compiled JavaScript.

## Step 4: Start Backend

### Development Mode (with auto-reload)

```bash
npm run dev
```

Expected output:
```
🚀 Server running on http://localhost:5000
✓ MongoDB connected
✓ Ready for requests
```

### Production Mode

```bash
npm start
```

## Step 5: Frontend Setup

Open a **new terminal** (keep backend running):

```bash
cd frontend
npm install
npm run dev
```

Expected output:
```
  VITE v5.x.x  ready in 123 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h + enter to show help
```

## Step 6: Test the RAG Chatbot

### 6.1 Open Browser

Navigate to: `http://localhost:5173/`

### 6.2 Click Chat Button

Look for "Elder Spirit Guide" button at bottom-right.

### 6.3 Send a Test Query

Ask any question about traditional knowledge:

- "What herbs help with digestion?"
- "Tell me about turmeric"
- "How to improve sleep naturally?"
- "What is yoga used for?"

### 6.4 Verify RAG Response

✅ You should see:
1. Typing animation while processing
2. Thoughtful response grounded in traditional knowledge
3. **Sources** shown below response (NEW!)
4. Response auto-plays audio

Example response:
> "Traditional wisdom recognizes turmeric as a powerful herb. Rich in curcumin, it has been used for centuries to reduce inflammation and support immunity. In Ayurveda, it's considered warming and supports digestive fire. Modern science confirms its anti-inflammatory properties—this is why adding black pepper (containing piperine) enhances absorption by up to 2000%!"
>
> **Sources:**
> - Home Remedies • Turmeric Milk (85%)
> - Ayurveda • Turmeric Root Powder (78%)

## Step 7: Verify Everything Works

### Check Backend Logs

Terminal where backend runs should show:
```
[RAG] Generating query embedding...
[RAG] Searching for similar content...
[RAG] Found 5 relevant sources, generating answer...
[RAG] Calling Gemini API...
✓ Response generated in 2341ms
```

### Check Browser Console

Press `F12` in browser, go to Console tab:
- No red errors
- Request to `http://localhost:5000/api/chat/query` shows success
- Response includes `sources` array

### Check API Response

Open browser DevTools → Network → find request to `/chat/query`:

```json
{
  "success": true,
  "data": {
    "response": "Traditional wisdom...",
    "sources": [
      {
        "title": "Turmeric Milk",
        "domain": "Home Remedies",
        "similarity": 0.85
      }
    ],
    "sessionId": "session_1234567890_abc",
    "responseTime": 2341
  }
}
```

## Troubleshooting

### Issue: "Gemini API key not configured"

**Solution:**
1. Check `.env` has `GEMINI_API_KEY=...`
2. Restart backend: Stop (Ctrl+C) and `npm run dev` again
3. Verify key is valid: Test at https://ai.google.dev/

### Issue: No Sources Shown

**Solution:**
1. Run embeddings again: `npm run generate-embeddings`
2. Check embeddings exist: `db.knowledgeembeddings.count()` should be > 0
3. Lower similarity threshold in code (future enhancement)

### Issue: Chat Returns Empty Response

**Solution:**
1. Check Gemini API key is valid
2. Check MongoDB is running
3. Check embeddings are generated
4. Monitor backend logs for errors

### Issue: MongoDB Connection Failed

**Solution:**
```bash
# Verify MongoDB is running
mongo --version

# Start MongoDB (if not running)
# macOS: brew services start mongodb-community
# Windows: Start MongoDB service
# Linux: sudo systemctl start mongod

# Test connection
mongo mongodb://127.0.0.1:27017/hackostic
```

### Issue: Slow Response Time

**Solution:**
1. Normal first time: ~3-5 seconds (embedding + search + generation)
2. Subsequent: ~2 seconds
3. If slower, check:
   - Internet connection
   - Gemini API quota usage
   - MongoDB query performance

### Issue: Frontend Can't Reach Backend

**Solution:**
1. Check `VITE_API_URL` in `frontend/.env` or code
2. Should be: `http://localhost:5000/api`
3. Verify backend is running on port 5000
4. Check CORS isn't blocking: Backend has `cors()` enabled

## Post-Setup

### Access Chat History API

Get previous conversations:

```bash
curl http://localhost:5000/api/chat/history/session_123456?limit=10
```

### Monitor Embeddings

Check database stats:

```bash
# MongoDB shell
use hackostic
db.knowledgeembeddings.countDocuments()
db.knowledgeembeddings.aggregate([
  { $group: { _id: "$domain", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### Update Knowledge Base

If you add new knowledge entries:

1. Add to `data/knowledge_base/chatbot_rag_knowledge_base.json`
2. Regenerate embeddings: `npm run generate-embeddings`
3. Backend will automatically use new embeddings

## Environment Checklist

- [ ] Node.js 16+ installed: `node --version`
- [ ] MongoDB running: `mongo --version`
- [ ] Gemini API key obtained and added to `.env`
- [ ] Backend dependencies installed: `npm install` in `backend/`
- [ ] Embeddings generated: `npm run generate-embeddings` completed
- [ ] Backend running: `npm run dev` shows "Server running on..."
- [ ] Frontend running: `npm run dev` shows local URL
- [ ] Browser can access: `http://localhost:5173`
- [ ] Chat works: Can send message and get response with sources

## Next Steps

1. **Customize Prompts**: Edit `backend/src/ai/prompts/ragPrompts.ts`
2. **Add More Knowledge**: Update JSON files in `data/knowledge_base/`
3. **Tune Retrieval**: Adjust `topK`, `similarityThreshold` in chat controller
4. **Monitor Performance**: Check response times and adjust as needed
5. **Deploy**: Use guide in main README for deployment

## Support

For detailed architecture info, see: [RAG_IMPLEMENTATION_GUIDE.md](./RAG_IMPLEMENTATION_GUIDE.md)

For general project info, see: [README.md](./README.md)

---

**Ready to chat!** 🚀

Once you complete these steps, open http://localhost:5173 and click the chat button to start asking questions about traditional knowledge. The Elder Spirit Guide is ready to serve!
