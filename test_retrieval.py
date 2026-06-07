from sentence_transformers import SentenceTransformer
import chromadb

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="documents/chroma_db")
collection = client.get_collection("jhu_unofficial_guide")

queries = [
    "What is the full-time graduate tuition?",
    "How do I request disability accommodations?",
    "What happens if I miss a registration deadline?",
]

for q in queries:
    emb = model.encode(q).tolist()
    results = collection.query(
        query_embeddings=[emb],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )
    print(f"\nQuery: {q}")
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0]
    ):
        print(f"  [{round(dist, 3)}] {meta['source']}")
        print(f"         {doc[:100]}...")