 ## 🎨 Interactive Architecture Diagrams

- [Vertical Flow Architecture](https://qualigenai.github.io/RAG-System/docs/architecture/RAG_Architecture_Interactive.html)
- [Data Flow Pipeline](https://qualigenai.github.io/RAG-System/docs/architecture/RAG_Architecture_DataFlow.html)

*(Best viewed in full screen)*

## 📊 Architecture

Our RAG system uses a sophisticated multi-layer architecture for optimal performance:

### Quick Overview
```
📤 Upload → ✂️ Chunk → 🧠 Embed → 💾 Index → 🔎 Search → 📄 Results
```

### Detailed Diagrams

We've created interactive architecture diagrams that you can explore:

1. **[Vertical Flow Architecture](docs/architecture/RAG_Architecture_Interactive.html)** - 
   Complete layer-by-layer breakdown with detailed components

2. **[Data Flow Pipeline](docs/architecture/RAG_Architecture_DataFlow.html)** - 
   Visual representation of data flow through the system

### System Design

- **Frontend:** Streamlit web interface
- **Backend:** FastAPI REST API
- **Core Engine:** Hybrid vector + BM25 search
- **Embeddings:** sentence-transformers (384-dim)
- **Storage:** In-memory with scalable options

For detailed architecture documentation, see [Architecture Docs](docs/architecture/README.md)
\# RAG System - Retrieval Augmented Generation



A complete, production-ready Retrieval Augmented Generation system built from scratch.



\## 🚀 Features



\- \*\*Semantic Search\*\* - Vector similarity (384-dim embeddings)

\- \*\*Keyword Search\*\* - BM25 algorithm

\- \*\*Hybrid Retrieval\*\* - Combined vector (70%) + keyword (30%) search

\- \*\*Document Upload\*\* - Support for PDF and TXT files

\- \*\*Web Interface\*\* - Streamlit-based chat UI

\- \*\*REST API\*\* - FastAPI backend for integration

\- \*\*Real-time Indexing\*\* - Documents indexed immediately upon upload



\## 📊 Performance



\- Query Response Time: < 500ms

\- Document Capacity: 1000+ documents

\- Embedding Dimension: 384

\- Supported Formats: PDF, TXT



\## 🏗️ Architecture

```

Frontend (Streamlit) ↔ Backend (FastAPI) ↔ RAG Engine

&nbsp;    ↓

Document Upload → Processing → Chunking → Embedding → Vector Store

&nbsp;    ↓

Query → Vector Search (70%) + BM25 (30%) → Hybrid Ranking → Results

```



\## 🛠️ Tech Stack



\- \*\*Backend:\*\* FastAPI, Uvicorn

\- \*\*Frontend:\*\* Streamlit

\- \*\*AI/ML:\*\* sentence-transformers, rank-bm25

\- \*\*Processing:\*\* LangChain, PyPDF

\- \*\*Language:\*\* Python 3.12



\## ⚡ Quick Start



\### Prerequisites

\- Python 3.12+

\- 4GB RAM

\- Internet connection



\### Installation (5 minutes)

```bash

\# Clone repository

git clone https://github.com/qualigenai/rag-system.git

cd rag-system



\# Create virtual environment

python -m venv venv

venv\\Scripts\\Activate.ps1  # Windows PowerShell



\# Install dependencies

pip install -r requirements.txt



\# Download embedding model

python -c "from sentence\_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2', cache\_folder='models')"

```



\### Running the System



\*\*Terminal 1 - Backend:\*\*

```bash

uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000

```



\*\*Terminal 2 - Frontend:\*\*

```bash

streamlit run src/ui/app.py

```



Open: http://localhost:8501



\## 📚 Documentation



\- \[Quick Start Guide](QUICK\_START\_GUIDE.md) - 5-minute setup

\- \[Full Documentation](RAG\_System\_Documentation.md) - Complete guide

\- \[Architecture Diagram](ARCHITECTURE\_DIAGRAM.md) - System design

\- \[Demo Script](DEMO\_SCRIPT.md) - Live demo walkthrough

\- \[Technical Specs](TECHNICAL\_SPECIFICATIONS.md) - Engineering details



\## 📋 Project Structure

```

rag-system/

├── src/

│   ├── core/                 # RAG core engine

│   │   ├── config.py        # Configuration

│   │   ├── embedder.py      # Embeddings

│   │   ├── vector\_db.py     # Vector storage

│   │   ├── bm25\_search.py   # Keyword search

│   │   ├── retriever.py     # Hybrid retrieval

│   │   └── loader.py        # Document loading

│   ├── api/                 # FastAPI backend

│   │   ├── main.py          # API server

│   │   └── models.py        # Data models

│   └── ui/                  # Streamlit frontend

│       └── app.py           # Web UI

├── data/                    # Documents directory

├── models/                  # Embedding models

├── logs/                    # System logs

├── requirements.txt         # Dependencies

├── .env                     # Configuration

└── README.md               # This file

```



\## 🔄 How It Works



\### 1. Document Upload

\- User uploads PDF or TXT file

\- System extracts text

\- Chunks document intelligently (500 char chunks)

\- Generates embeddings for each chunk

\- Indexes in vector database \& BM25



\### 2. Query Processing

\- User asks a question

\- Question embedded to 384-dim vector

\- \*\*Vector Search (70%):\*\* Find semantically similar documents

\- \*\*BM25 Search (30%):\*\* Find keyword matches

\- Combine scores with weighting

\- Return top-K ranked results



\### 3. Answer Generation

\- Retrieved documents displayed to user

\- Similarity scores shown

\- Can add LLM integration for auto-answers (v1.5)



\## 📊 API Endpoints

```

GET  /health          - System health check

GET  /stats          - System statistics

POST /query          - Search documents

POST /upload         - Upload new document

POST /clear          - Clear all documents

```



See \[Technical Specifications](TECHNICAL\_SPECIFICATIONS.md) for details.



\## 🚀 Roadmap



\*\*v1.0\*\* ✅ Current

\- Core RAG system

\- Document search

\- Hybrid retrieval



\*\*v1.5\*\* ⏳ Next

\- LLM integration (Ollama/Claude)

\- Response generation

\- Chat history



\*\*v2.0\*\* 🔄 Planned

\- Database persistence

\- User authentication

\- Multi-tenant support

\- Advanced analytics



\*\*v2.5+\*\* 🎯 Future

\- Distributed vector store

\- Load balancing

\- Admin dashboard

\- Custom models



\## 💡 Use Cases



\- 📚 Knowledge Base Search

\- 🏢 Internal Documentation

\- 📖 Customer Support FAQ

\- 🔬 Research Assistant

\- 📊 Business Analytics

\- ⚖️ Legal Discovery



\## 🔒 Security (v1.0)



\- ✅ Input validation (Pydantic)

\- ✅ Type safety (Python hints)

\- ⚠️ Local storage (no external APIs)

\- 🔄 Authentication (planned v2)

\- 🔄 Rate limiting (planned v2)



\## 📈 Performance Metrics



| Metric | Value |

|--------|-------|

| Query Latency | < 500ms |

| Document Capacity | 1000s |

| Embedding Dim | 384 |

| Storage per 1K docs | ~300MB |

| Memory per 1K docs | ~200MB |



\## 🤝 Contributing



This is a demonstration project. Contributions welcome!



1\. Fork the repository

2\. Create a feature branch

3\. Commit your changes

4\. Push to the branch

5\. Create a Pull Request



\## 📝 License



MIT License - see LICENSE file for details



\## 👨‍💻 Author



Built by \*\*Rambhupal\*\* | qualigenai



\## 🆘 Support



\- Check \[QUICK\_START\_GUIDE.md](QUICK\_START\_GUIDE.md) for setup issues

\- See \[RAG\_System\_Documentation.md](RAG\_System\_Documentation.md) for detailed guide

\- Review \[DEMO\_SCRIPT.md](DEMO\_SCRIPT.md) for demo walkthrough



\## 📞 Contact



GitHub: \[@qualigenai](https://github.com/qualigenai)



---



\*\*Building the future of AI-powered search\*\* 🚀



This is a complete, production-ready RAG implementation suitable for:

\- Learning RAG concepts

\- Building enterprise search systems

\- Integrating into existing applications

\- Scaling to production use cases

