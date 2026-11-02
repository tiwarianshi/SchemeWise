
from services.embedding_service import embed_text
from services.vector_store_service import VectorStoreService

DOCUMENT_ID = "38ff4141-ec42-4592-8ae0-d3110d7967ff"

question = "What skills and qualifications are mentioned in this resume?"

# Convert the question into an embedding.
query_embedding = embed_text(question)

# Search ChromaDB, restricted to the uploaded document.
vector_store = VectorStoreService()

results = vector_store.query_chunks(
    query_embedding=query_embedding,
    n_results=5,
    document_id=DOCUMENT_ID,
)

print("Total stored chunks:", vector_store.count())
print("Retrieved chunks:", len(results))

for index, result in enumerate(results, start=1):
    print(f"\n--- Result {index} ---")
    print("Distance:", result["distance"])
    print("Metadata:", result["metadata"])
    print("Text:", result["text"][:700])
