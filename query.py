"""
query.py
Takes a user question, retrieves top-5 chunks from ChromaDB,
passes them to the Groq API with a grounding-enforcing system prompt,
and returns the answer with source citations.
"""

import os
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

CHROMA_DIR = "documents/chroma_db"
COLLECTION_NAME = "jhu_unofficial_guide"
TOP_K = 5

# Load model and ChromaDB
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_collection(COLLECTION_NAME)

# Load Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a helpful assistant for Johns Hopkins University graduate students.
Answer the user's question using ONLY the context provided below.
Do not use any outside knowledge. If the answer is not in the context, say so clearly.
At the end of your answer, always list the source documents you drew from under a "Sources:" heading.
Be concise and direct."""


def query(question: str, verbose: bool = False) -> dict:
    # Embed the question
    question_embedding = model.encode(question).tolist()

    # Retrieve top-k chunks
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=TOP_K,
    )

    chunks = results["documents"][0]
    metadatas = results["metadatas"][0]

    # Build context string
    context_parts = []
    for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
        context_parts.append(f"[{i+1}] Source: {meta['source']}\n{chunk}")
    context = "\n\n---\n\n".join(context_parts)

    if verbose:
        print("\n--- RETRIEVED CHUNKS ---")
        for i, (chunk, meta) in enumerate(zip(chunks, metadatas)):
            print(f"\n[{i+1}] {meta['source']}")
            print(chunk[:200] + "...")

    # Call Groq API
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.1,
        max_tokens=1000,
    )

    answer = response.choices[0].message.content

    return {
        "question": question,
        "answer": answer,
        "sources": [m["source"] for m in metadatas],
        "chunks": chunks,
    }


if __name__ == "__main__":
    print("JHU Unofficial Guide -- Query Interface")
    print("Type 'quit' to exit.\n")

    while True:
        question = input("Your question: ").strip()
        if question.lower() in ("quit", "exit", "q"):
            break
        if not question:
            continue

        result = query(question, verbose=True)
        print(f"\nAnswer:\n{result['answer']}\n")
        print("-" * 60)
