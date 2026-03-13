# RAG Implementation - Quick Reference Guide

## 📋 Pre-Start Checklist (Do This First - 30 minutes)

```bash
# 1. Verify Python
python --version  # Need 3.9+

# 2. Create project
mkdir rag-system && cd rag-system
git init

# 3. Setup environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 4. Create .env file
cat > .env << EOF
DEBUG=True
EMBEDDING_MODEL=all-MiniLM-L6-v2
CHUNK_SIZE=500
LLM_PROVIDER=local
LLM_MODEL=mistral
QDRANT_URL=http://localhost:6333
EOF

# 5. Create requirements.txt (copy from main guide)
# Then: pip install -r requirements.txt
```

---

## ⏱️ Daily Timeline (5-8 hours/day)

### WEEK 1: FOUNDATION

#### Day 1-2: Environment & Dependencies (2-3 hours)
```bash
# What to do:
[ ] Create requirements.txt
[ ] Install all packages
[ ] Create .env file
[ ] Create config.py
[ ] Test imports

# By end: All libraries installed and verified ✅
```

#### Day 3-4: Embedding & Vector DB (4-5 hours)
```bash
# What to do:
[ ] Create embedder.py (sentence-transformers)
[ ] Create vector_db.py (Qdrant)
[ ] Download embedding model (~130MB)
[ ] Test embedding generation
[ ] Setup Qdrant

# By end: Embedding system working ✅
# Run: python -c "from src.core.embedder import EmbeddingManager; m = EmbeddingManager(); print(m.embed_text('test').shape)"
```

#### Day 5-6: Document Processing (4-5 hours)
```bash
# What to do:
[ ] Create loader.py (document loading)
[ ] Implement text loading
[ ] Implement PDF loading
[ ] Implement chunking strategy
[ ] Create BM25 retriever

# By end: Can load and chunk documents ✅
# Test: python src/core/loader.py
```

---

### WEEK 2: INTEGRATION

#### Day 7-8: Retrieval System (3-4 hours)
```bash
# What to do:
[ ] Create hybrid retriever (vector + BM25)
[ ] Implement combining logic
[ ] Test retrieval quality
[ ] Optimize chunk size

# By end: Hybrid retrieval working ✅
# Test: python src/core/retriever.py
```

#### Day 9-10: LLM Integration (5-6 hours)
```bash
# What to do:
[ ] Create generator.py
[ ] Add Ollama support (local)
[ ] Add Claude API support (optional)
[ ] Add OpenAI support (optional)
[ ] Test LLM generation

# Note: For local Ollama:
ollama pull mistral
ollama serve  # Start in separate terminal

# By end: LLM generating responses ✅
```

#### Day 11-12: FastAPI Backend (4-5 hours)
```bash
# What to do:
[ ] Create FastAPI app (main.py)
[ ] Add query endpoint
[ ] Add upload endpoint
[ ] Add health endpoint
[ ] Test API endpoints

# Start API:
python -m uvicorn src.api.main:app --reload --port 8000

# Test:
curl http://localhost:8000/health
curl -X POST http://localhost:8000/query -H "Content-Type: application/json" -d '{"query":"test"}'

# By end: API working and documented ✅
```

---

### WEEK 3: PRODUCTION

#### Day 13-14: Web UI & Testing (4-5 hours)
```bash
# What to do:
[ ] Create Streamlit app (app.py)
[ ] Build chat interface
[ ] Add file upload
[ ] Test all features
[ ] Add error handling

# Start UI:
streamlit run src/ui/app.py

# Access: http://localhost:8501

# By end: Full web interface working ✅
```

#### Day 15-16: Docker & Deployment (3-4 hours)
```bash
# What to do:
[ ] Create Dockerfile
[ ] Create docker-compose.yml
[ ] Setup multi-container orchestration
[ ] Test Docker build
[ ] Verify all services start

# Build and run:
docker-compose up --build

# By end: Containerized and deployable ✅
```

#### Day 17-18: Monitoring & Polish (3-4 hours)
```bash
# What to do:
[ ] Add logging system
[ ] Create analytics endpoint
[ ] Add health checks
[ ] Setup monitoring
[ ] Create documentation

# By end: Production-ready system ✅
```

#### Day 19-21: Testing & Deployment (5-6 hours)
```bash
# What to do:
[ ] Run full test suite
[ ] Performance testing
[ ] Security audit
[ ] Create README & DEPLOYMENT guides
[ ] Deploy to cloud (optional)

# By end: Ready to go live ✅
```

---

## 📊 File Structure You'll Create

```
rag-system/
├── venv/                          # Virtual environment
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py             # Configuration ✅ Day 1
│   │   ├── embedder.py           # Embeddings ✅ Day 3
│   │   ├── vector_db.py          # Qdrant ✅ Day 3
│   │   ├── bm25_search.py        # BM25 ✅ Day 5
│   │   ├── retriever.py          # Hybrid retrieval ✅ Day 7
│   │   ├── generator.py          # LLM ✅ Day 9
│   │   ├── loader.py             # Document loading ✅ Day 5
│   │   ├── monitoring.py         # Logging ✅ Day 17
│   │   └── healthcheck.py        # Health checks ✅ Day 17
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app ✅ Day 11
│   │   └── models.py             # Pydantic models ✅ Day 11
│   │
│   └── ui/
│       ├── __init__.py
│       └── app.py                # Streamlit ✅ Day 13
│
├── tests/
│   └── test_rag.py               # Unit tests ✅ Day 15
│
├── data/                          # Your documents (create these)
├── models/                        # Downloaded models
├── logs/                          # Application logs
│
├── requirements.txt               # Python packages ✅ Day 1
├── .env                          # Configuration ✅ Day 1
├── Dockerfile                     # Container image ✅ Day 15
├── docker-compose.yml            # Orchestration ✅ Day 15
├── Dockerfile.streamlit          # Streamlit container ✅ Day 15
├── README.md                      # Documentation ✅ Day 17
├── DEPLOYMENT.md                 # Deploy guide ✅ Day 17
└── deploy.sh                      # Deploy script ✅ Day 19
```

---

## 🚀 Command Reference

### Quick Start from Scratch
```bash
# 1. Setup (30 min)
mkdir rag-system && cd rag-system
python -m venv venv
source venv/bin/activate
pip install sentence-transformers qdrant-client langchain fastapi uvicorn streamlit

# 2. Download model (5 min)
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# 3. Setup Ollama (optional, for local LLM)
# Install from https://ollama.ai
ollama pull mistral
ollama serve  # Start in terminal 1

# 4. Start API (in terminal 2)
python -m uvicorn src.api.main:app --reload

# 5. Start UI (in terminal 3)
streamlit run src/ui/app.py

# 6. Test
curl http://localhost:8000/health  # Should return 200
# Open http://localhost:8501 in browser
```

### Local Development
```bash
# Activate environment
source venv/bin/activate

# Run API with auto-reload
uvicorn src.api.main:app --reload --port 8000

# Run Streamlit
streamlit run src/ui/app.py

# Run tests
pytest tests/ -v

# Check system health
python -c "from src.core.healthcheck import SystemHealthCheck; print(SystemHealthCheck().check_all())"
```

### Docker Production
```bash
# Build and start all services
docker-compose up --build

# View logs
docker-compose logs -f api
docker-compose logs -f ui
docker-compose logs -f qdrant

# Stop all
docker-compose down

# Clean up
docker-compose down -v  # Remove volumes too
```

### Testing & Monitoring
```bash
# Unit tests
pytest tests/ -v --cov=src

# Load testing
pip install locust
# Create locustfile.py with test scenarios

# Performance monitoring
# Check logs/queries.jsonl for query analytics
python -c "
import json
with open('logs/queries.jsonl') as f:
    queries = [json.loads(line) for line in f]
    print(f'Total: {len(queries)}')
    print(f'Avg latency: {sum(q[\"duration_seconds\"] for q in queries)/len(queries):.2f}s')
"
```

---

## ⚠️ Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'sentence_transformers'"
```bash
# Solution:
pip install sentence-transformers
# Or install all: pip install -r requirements.txt
```

### Issue: "ConnectionError: Cannot connect to Qdrant"
```bash
# Solution: Qdrant is not running or not accessible
# Check if using in-memory mode:
from qdrant_client import QdrantClient
client = QdrantClient(":memory:")  # In-memory (no external service needed)
```

### Issue: "Ollama not responding"
```bash
# Solution: Ollama not running
# Make sure you have 2 terminals:
# Terminal 1: ollama serve
# Terminal 2: python -m uvicorn src.api.main:app --reload

# Or check port 11434:
curl http://localhost:11434/api/generate
```

### Issue: "Out of memory" error
```bash
# Solution: Reduce chunk size or model size
# In .env:
CHUNK_SIZE=250  # Reduce from 500
# Or use smaller embedding model:
EMBEDDING_MODEL=all-MiniLM-L6-v2  # This is already small
# Or use quantized Ollama model:
ollama pull mistral:7b-instruct-q4  # 4-bit quantized
```

### Issue: "Slow embeddings"
```bash
# Solution: Use GPU acceleration
# In embedder.py, change:
device="cuda"  # Instead of "cpu"

# Check GPU:
python -c "import torch; print(torch.cuda.is_available())"
```

### Issue: "Streamlit can't connect to API"
```bash
# Solution: API not running on port 8000
# Make sure to run:
python -m uvicorn src.api.main:app --reload --port 8000

# Check if running:
curl http://localhost:8000/health
```

---

## 📈 Progress Tracking

### Week 1 Checklist
- [ ] Day 1: Environment setup ✅
- [ ] Day 2: Dependencies installed ✅
- [ ] Day 3: Embedding system ✅
- [ ] Day 4: Vector DB ✅
- [ ] Day 5: Document loading ✅
- [ ] Day 6: Chunking & BM25 ✅

**Week 1 Goal:** Core RAG system functional

### Week 2 Checklist
- [ ] Day 7: Hybrid retrieval ✅
- [ ] Day 8: LLM integration ✅
- [ ] Day 9: FastAPI backend ✅
- [ ] Day 10: API testing ✅
- [ ] Day 11: Streamlit UI ✅
- [ ] Day 12: UI testing ✅

**Week 2 Goal:** Full user-facing system

### Week 3 Checklist
- [ ] Day 13: Docker setup ✅
- [ ] Day 14: Containerization ✅
- [ ] Day 15: Testing ✅
- [ ] Day 16: Monitoring ✅
- [ ] Day 17: Documentation ✅
- [ ] Day 18: Deployment ✅

**Week 3 Goal:** Production-ready deployment

---

## 💡 Key Decisions to Make

### 1. LLM Provider (Day 9)
```
Local (Ollama):
✅ Free, runs locally
❌ Slower, lower quality
Use if: You want zero cost

Claude API:
✅ High quality, fast
❌ Costs ~$0.003-0.01 per query
Use if: You want best quality

OpenAI (GPT):
✅ Good quality, proven
❌ Similar cost to Claude
Use if: You prefer OpenAI

Default: Start with Ollama, switch to Claude for better results
```

### 2. Vector DB (Day 4)
```
In-memory Qdrant:
✅ Easy to start, no setup
❌ Resets on restart, single instance
Use if: Testing/development

Qdrant Server:
✅ Persistent, scalable
❌ Need Docker/server
Use if: Production

Pinecone Cloud:
✅ Managed, scalable
❌ ~$0-50/month
Use if: Don't want to manage infrastructure

Default: Start with in-memory, upgrade to server later
```

### 3. Documents (Day 5)
```
Start with:
- 10-50 documents for testing
- Mix of text and PDF
- Different document types
- Known Q&A pairs for testing

Where to get:
- Wikipedia articles (public domain)
- Your own documentation
- Sample datasets
- Open source books
```

---

## 📊 Expected Performance

By Day 10 (End of Week 2):
```
Response Latency: 2-5 seconds
├─ Embedding: 100ms
├─ Retrieval: 300-500ms
└─ LLM Generation: 1-2s

Accuracy (for test queries): 70-85%
Memory Usage: 2-4GB
Disk Usage: 5-10GB

Bottleneck: LLM generation (1-2s)
Next optimization: Faster LLM (using Claude)
```

By Day 18 (End of Week 3):
```
Response Latency: 1-3 seconds (with API calls optimized)
Throughput: 100+ QPS per server
Accuracy: 80-90% (with better prompts)
Memory: Optimized to 1-2GB
Uptime: 99%+

System fully production-ready
```

---

## 🎓 Learning Path

### You'll Learn:
1. **Vector embeddings** - How to convert text to vectors
2. **Similarity search** - Finding relevant documents quickly
3. **Hybrid retrieval** - Combining vector + keyword search
4. **LLM prompting** - Getting good answers from LLMs
5. **API design** - Building REST APIs
6. **Frontend development** - Creating web UIs
7. **Containerization** - Dockerizing applications
8. **System design** - Building scalable systems

### Resources to Reference:
- **Vector Databases:** https://www.pinecone.io/learn/vector-database/
- **Embeddings:** https://www.sbert.net/
- **RAG Papers:** "Retrieval-Augmented Generation for Knowledge-Intensive NLP"
- **FastAPI:** https://fastapi.tiangolo.com/
- **Streamlit:** https://docs.streamlit.io/

---

## 🎯 Success Criteria

**Day 3:** ✅ Embeddings working
**Day 6:** ✅ Full document pipeline
**Day 10:** ✅ Full RAG query working
**Day 14:** ✅ Web UI functional
**Day 18:** ✅ Docker deployment
**Day 21:** ✅ Production ready

---

## 💰 Cost Summary (After Implementation)

```
Development: $0 (free tools)
Hosting: $5-20/month (VPS like DigitalOcean)
LLM APIs: $0-50/month (optional, depends on usage)
─────────────────────────
Monthly: $5-70/month

Compare to enterprise RAG: $1000+/month
Your system: Just 0.5% of the cost!
```

---

**Ready? Start with Day 1: Environment Setup** 🚀

Open `Step_by_Step_RAG_Implementation.md` for detailed Day-by-Day guide with complete code examples.
