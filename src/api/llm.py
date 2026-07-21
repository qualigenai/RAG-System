from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client — free, no credits needed
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_answer(question: str, chunks: list) -> str:
    """
    RAG System v2.0 — Answer generation using Groq llama-3.1-8b-instant.
    Replaces OpenAI GPT-4o-mini (v1.5) with free Groq LLM.
    Model  : llama-3.1-8b-instant
    Cost   : Free — no API credits needed
    """
    if not chunks:
        return "No relevant documents found. Please upload documents first."

    # Build context from chunks
    context = "\n\n".join([
        f"From {chunk.get('source', 'Unknown Document')}:\n{chunk.get('text', '')[:300]}"
        for chunk in chunks[:3]
    ])

    system_prompt = """You are a helpful AI assistant that answers questions based on provided documents.
IMPORTANT RULES:
1. Answer ONLY based on the provided context
2. If the answer is not in the documents, say "This information is not available in the provided documents"
3. Be clear, concise, and very professional
4. Reference which document you are using when possible"""

    user_message = f"""Context from uploaded documents:
{context}

User Question: {question}

Please answer based ONLY on the provided context above."""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error generating answer: {str(e)}"