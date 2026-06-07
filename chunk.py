"""
chunk.py
Loads processed JSON documents from documents/processed/,
splits each into chunks using LangChain's RecursiveCharacterTextSplitter,
and saves all chunks to documents/chunks.json.

Chunk size: 500 tokens (approximated as characters * 4)
Overlap: 75 tokens
"""

import json
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

PROCESSED_DIR = Path("documents/processed")
OUTPUT_FILE = Path("documents/chunks.json")

# Token approximation: 1 token ~ 4 characters
# 500 tokens ~ 2000 characters, 75 tokens ~ 300 characters
CHUNK_SIZE = 2000
CHUNK_OVERLAP = 300

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def chunk_documents():
    all_chunks = []

    for json_file in sorted(PROCESSED_DIR.glob("*.json")):
        with open(json_file, "r", encoding="utf-8") as f:
            doc = json.load(f)

        source = doc["source"]
        text = doc["text"]

        if not text.strip():
            print(f"[SKIP] {source} -- empty text")
            continue

        raw_chunks = splitter.split_text(text)

        # Filter out empty or very short chunks
        chunks = [c for c in raw_chunks if len(c.strip()) > 50]

        for i, chunk_text in enumerate(chunks):
            all_chunks.append({
                "chunk_id": f"{json_file.stem}_{i}",
                "source": source,
                "text": chunk_text.strip(),
                "char_count": len(chunk_text.strip()),
            })

        print(f"[{source}] -> {len(chunks)} chunks")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)

    print(f"\nTotal chunks: {len(all_chunks)}")
    print(f"Saved to {OUTPUT_FILE}")

    # Print 5 sample chunks for inspection
    print("\n--- 5 SAMPLE CHUNKS ---")
    import random
    samples = random.sample(all_chunks, min(5, len(all_chunks)))
    for i, chunk in enumerate(samples):
        print(f"\n[Sample {i+1}] source: {chunk['source']}")
        print(f"chars: {chunk['char_count']}")
        print(chunk['text'][:300])
        print("...")


if __name__ == "__main__":
    chunk_documents()