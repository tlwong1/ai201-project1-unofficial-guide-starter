"""
embed.py
Loads chunks from documents/chunks.json, embeds each using
all-MiniLM-L6-v2 via sentence-transformers, and stores them
in a local ChromaDB collection with source metadata.
Runs a test query at the end to verify retrieval is working.
"""

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb

CHUNKS_FILE = Path("documents/chunks.json")
CHROMA_DIR = Path("documents/chroma_db")
COLLECTION_NAME = "jhu_unofficial_guide"

# Load embedding model
print("Loading embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load chunks
print(f"Loading chunks from {CHUNKS_FILE}...")
with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Loaded {len(chunks)} chunks.")

# Set up ChromaDB
print(f"Setting up ChromaDB at {CHROMA_DIR}...")
client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# Delete existing collection if it exists (for clean reruns)
existing = [c.name for c in client.list_collections()]
if COLLECTION_NAME in existing:
    print(f"Deleting existing collection '{COLLECTION_NAME}'...")
    client.delete_collection(COLLECTION_NAME)

collection = client.create_collection(COLLECTION_NAME)

# Embed and store in batches
BATCH_SIZE = 50
total = len(chunks)

print(f"Embedding and storing {total} chunks in batches of {BATCH_SIZE}...")

for i in range(0, total, BATCH_SIZE):
    batch = chunks[i:i + BATCH_SIZE]

    texts = [c["text"] for c in batch]
    ids = [c["chunk_id"] for c in batch]
    metadatas = [{"source": c["source"]} for c in batch]

    embeddings = model.encode(texts, show_progress_bar=False).tolist()

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    print(f"  Stored chunks {i+1} to {min(i+BATCH_SIZE, total)}")

print(f"\nDone. {total} chunks stored in ChromaDB collection '{COLLECTION_NAME}'.")

# --- Test retrieval ---
print("\n--- TEST RETRIEVAL ---")
TEST_QUERIES = [
    "What is the full-time graduate tuition?",
    "How do I request disability accommodations?",
    "What happens if I miss a registration deadline?",
]

for query in TEST_QUERIES:
    query_embedding = model.encode(query).tolist()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
    )

    print(f"\nQuery: {query}")
    for j, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
        print(f"  [{j+1}] source: {meta['source']}")
        print(f"       {doc[:150]}...")
