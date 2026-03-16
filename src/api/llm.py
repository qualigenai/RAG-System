from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_answer(question: str, chunks: list) -> str:
    """
    Generate an answer using GPT-4 based on retrieved chunks

    Args:
        question: User's question
        chunks: List of retrieved document chunks

    Returns:
        AI-generated answer
    """

    if not chunks:
        return "No relevant documents found. Please upload documents first."

    # Build context from chunks
    context = "\n\n".join([
         f"From {chunk.get('source', 'Unknown Document')}:\n{chunk.get('text', '')[:300]}"
    for chunk in chunks[:3]  # Use top 3 chunks
    ])

    # System prompt
    system_prompt = """You are a helpful AI assistant that answers questions based on provided documents.

IMPORTANT RULES:
1. Answer ONLY based on the provided context
2. If the answer is not in the documents, say "This information is not available in the provided documents"
3. Be clear, concise, and professional
4. Reference which document you're using when possible"""

    # User message
    user_message = f"""Context from uploaded documents:

{context}

User Question: {question}

Please answer based ONLY on the provided context above."""

    try:
        # Call GPT-4
        response = client.chat.completions.create(
            model="gpt-4o-mini",
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