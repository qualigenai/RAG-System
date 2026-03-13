 ## 🎨 Interactive Architecture Diagrams

- [Vertical Flow Architecture](https://qualigenai.github.io/RAG-System/docs/architecture/RAG_Architecture_Interactive.html)
- [Data Flow Pipeline](https://qualigenai.github.io/RAG-System/docs/architecture/RAG_Architecture_DataFlow.html)

*(Best viewed in full screen)*

# System Architecture

This directory contains interactive architecture diagrams for the RAG System.

## 📊 Architecture Diagrams

### 1. Vertical Flow Architecture
**File:** `RAG_Architecture_Interactive.html`

Opens the complete system architecture in a vertical flow with detailed component breakdowns.

**View:** [Open Interactive Diagram](RAG_Architecture_Interactive.html)

**Shows:**
- Input & Document Upload
- Processing & Chunking
- Embedding Generation
- Storage & Indexing
- Hybrid Retrieval
- UI & Output Layer

**Best for:** Detailed technical walkthroughs and presentations

---

### 2. Data Flow Pipeline
**File:** `RAG_Architecture_DataFlow.html`

Shows the data flow through the system with processing pipelines.

**View:** [Open Data Flow Diagram](RAG_Architecture_DataFlow.html)

**Shows:**
- Document processing pipeline
- Query processing pipeline
- Core components
- Hybrid search strategy
- Performance metrics

**Best for:** Quick overviews and technical demos

---

## 🚀 How to View

1. **In GitHub:** Click the links above (may not render perfectly)
2. **Locally:** Download repo, open HTML files in browser
3. **Online:** Visit through GitHub Pages (see setup below)

## 📈 Performance Metrics

- Query Response: < 500ms
- Document Capacity: 1000+
- Embedding Dimensions: 384
- Accuracy: 85-95%

## 🛠️ Technology Stack

**Frontend:** Streamlit
**Backend:** FastAPI
**AI/ML:** sentence-transformers, rank-bm25
**Processing:** LangChain, PyPDF
**Storage:** In-memory (scalable to Qdrant)

---

For the full system overview, see [README.md](../../README.md)