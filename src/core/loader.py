from pathlib import Path
from typing import List, Dict, Optional
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.core.config import settings

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Load and process documents"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_text_files(self, directory: str) -> List[Dict]:
        """Load all .txt files from directory"""
        docs = []
        path = Path(directory)
        
        if not path.exists():
            logger.warning(f"Directory {directory} does not exist")
            return docs
        
        for file_path in path.glob("**/*.txt"):
            logger.info(f"Loading {file_path}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if content.strip():  # Only add if content is not empty
                    docs.append({
                        "text": content,
                        "source": str(file_path),
                        "metadata": {"type": "text"}
                    })
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
        
        logger.info(f"Loaded {len(docs)} text files")
        return docs
    
    def load_pdf_files(self, directory: str) -> List[Dict]:
        """Load all .pdf files from directory"""
        docs = []
        path = Path(directory)
        
        if not path.exists():
            logger.warning(f"Directory {directory} does not exist")
            return docs
        
        try:
            from pypdf import PdfReader
        except ImportError:
            logger.warning("PyPDF2 not installed. Skipping PDF loading.")
            return docs
        
        for file_path in path.glob("**/*.pdf"):
            logger.info(f"Loading PDF {file_path}")
            
            try:
                reader = PdfReader(str(file_path))
                content = ""
                for page in reader.pages:
                    content += page.extract_text() + "\n"
                
                if content.strip():
                    docs.append({
                        "text": content,
                        "source": str(file_path),
                        "metadata": {"type": "pdf", "pages": len(reader.pages)}
                    })
            except Exception as e:
                logger.error(f"Error loading PDF {file_path}: {e}")
        
        logger.info(f"Loaded {len(docs)} PDF files")
        return docs
    
    def chunk_documents(self, documents: List[Dict]) -> List[Dict]:
        """Split documents into chunks"""
        chunked_docs = []
        
        for doc in documents:
            text = doc["text"]
            source = doc["source"]
            
            # Split text into chunks
            chunks = self.splitter.split_text(text)
            
            logger.info(f"Split '{source}' into {len(chunks)} chunks")
            
            for chunk_id, chunk_text in enumerate(chunks):
                chunked_docs.append({
                    "text": chunk_text,
                    "source": source,
                    "chunk_id": chunk_id,
                    "metadata": doc.get("metadata", {})
                })
        
        logger.info(f"Created {len(chunked_docs)} chunks total")
        return chunked_docs
    
    def process_directory(self, directory: str) -> List[Dict]:
        """Load and chunk all documents from directory"""
        # Load documents
        docs = []
        docs.extend(self.load_text_files(directory))
        docs.extend(self.load_pdf_files(directory))
        
        if not docs:
            logger.warning(f"No documents found in {directory}")
            return []
        
        # Chunk documents
        chunked = self.chunk_documents(docs)
        
        return chunked

# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    processor = DocumentProcessor()
    
    # Create sample data
    Path("data").mkdir(exist_ok=True)
    
    sample_text = """Retrieval-Augmented Generation (RAG)

RAG is a technique that combines retrieval and generation.
It retrieves relevant documents and uses them to generate responses.

Key benefits:
- Reduces hallucination
- Provides up-to-date information
- Allows fact checking

How RAG works:
1. User asks a question
2. System retrieves relevant documents
3. System generates answer based on documents
4. Answer is returned to user"""
    
    with open("data/sample.txt", "w") as f:
        f.write(sample_text)
    
    # Process
    chunks = processor.process_directory("data")
    print(f"Total chunks: {len(chunks)}")
    if chunks:
        print(f"\nFirst chunk:")
        print(f"Source: {chunks[0]['source']}")
        print(f"Text: {chunks[0]['text'][:100]}...")
    print("✅ Document loading test passed!")