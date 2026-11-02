
from pathlib import Path

import chromadb


SERVER_DIR = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = SERVER_DIR / "storage" / "chroma_db"

COLLECTION_NAME = "scheme_document_chunks"
EMBEDDING_DIMENSIONS = 768


class VectorStoreService:
    """
    Stores and retrieves document chunks using Gemini embeddings
    and a persistent local ChromaDB collection.
    """

    def __init__(self, db_path: str | Path | None = None):
        storage_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        storage_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.PersistentClient(
            path=str(storage_path)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    @staticmethod
    def _validate_embedding(embedding: list[float]) -> list[float]:
        if not isinstance(embedding, list):
            raise ValueError("Embedding must be a list.")

        if len(embedding) != EMBEDDING_DIMENSIONS:
            raise ValueError(
                f"Embedding must contain exactly "
                f"{EMBEDDING_DIMENSIONS} dimensions."
            )

        try:
            vector = [float(value) for value in embedding]
        except (TypeError, ValueError) as error:
            raise ValueError(
                "Embedding must contain numeric values."
            ) from error

        return vector

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
        scheme_id: str | None = None,
        document_name: str | None = None,
        source_url: str | None = None,
    ) -> int:
        """Add or update document chunks and their embeddings."""

        if not isinstance(chunks, list):
            raise ValueError("chunks must be a list.")

        if not isinstance(embeddings, list):
            raise ValueError("embeddings must be a list.")

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Number of chunks and embeddings must match."
            )

        if not chunks:
            return 0

        ids = []
        documents = []
        metadatas = []
        vectors = []

        for index, (chunk, embedding) in enumerate(
            zip(chunks, embeddings)
        ):
            if not isinstance(chunk, dict):
                raise ValueError(
                    f"Chunk at index {index} must be a dictionary."
                )

            document_id = chunk.get("document_id")
            page_number = chunk.get("page_number")
            chunk_index = chunk.get("chunk_index")
            text = chunk.get("text")

            if not isinstance(document_id, str) or not document_id.strip():
                raise ValueError(
                    f"Chunk at index {index} has an invalid document_id."
                )

            if (
                not isinstance(page_number, int)
                or isinstance(page_number, bool)
                or page_number < 1
            ):
                raise ValueError(
                    f"Chunk at index {index} has an invalid page_number."
                )

            if (
                not isinstance(chunk_index, int)
                or isinstance(chunk_index, bool)
                or chunk_index < 0
            ):
                raise ValueError(
                    f"Chunk at index {index} has an invalid chunk_index."
                )

            if not isinstance(text, str) or not text.strip():
                raise ValueError(
                    f"Chunk at index {index} has empty text."
                )

            metadata = {
                "document_id": document_id,
                "page_number": page_number,
                "chunk_index": chunk_index,
            }

            page_chunk_index = chunk.get("page_chunk_index")
            token_count = chunk.get("token_count")

            if page_chunk_index is not None:
                if (
                    not isinstance(page_chunk_index, int)
                    or isinstance(page_chunk_index, bool)
                    or page_chunk_index < 0
                ):
                    raise ValueError("Invalid page_chunk_index.")
                metadata["page_chunk_index"] = page_chunk_index

            if token_count is not None:
                if (
                    not isinstance(token_count, int)
                    or isinstance(token_count, bool)
                    or token_count < 0
                ):
                    raise ValueError("Invalid token_count.")
                metadata["token_count"] = token_count

            if scheme_id is not None:
                metadata["scheme_id"] = str(scheme_id)

            if document_name is not None:
                metadata["document_name"] = str(document_name)

            if source_url is not None:
                metadata["source_url"] = str(source_url)

            ids.append(f"{document_id}:{chunk_index}")
            documents.append(text)
            metadatas.append(metadata)
            vectors.append(self._validate_embedding(embedding))

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=vectors,
        )

        return len(ids)

    def query_chunks(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        scheme_id: str | None = None,
        document_id: str | None = None,
    ) -> list[dict]:
        """Find the most similar chunks for a query embedding."""

        if (
            not isinstance(n_results, int)
            or isinstance(n_results, bool)
            or n_results < 1
        ):
            raise ValueError("n_results must be a positive integer.")

        total_chunks = self.collection.count()

        if total_chunks == 0:
            return []

        where_filter = None

        filters = []

        if scheme_id is not None:
            filters.append({"scheme_id": str(scheme_id)})

        if document_id is not None:
            filters.append({"document_id": str(document_id)})

        if len(filters) == 1:
            where_filter = filters[0]
        elif len(filters) > 1:
            where_filter = {"$and": filters}

        results = self.collection.query(
            query_embeddings=[
                self._validate_embedding(query_embedding)
            ],
            n_results=min(n_results, total_chunks),
            where=where_filter,
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        retrieved_chunks = []

        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for chunk_id, text, metadata, distance in zip(
            ids, documents, metadatas, distances
        ):
            retrieved_chunks.append({
                "id": chunk_id,
                "text": text,
                "metadata": metadata,
                "distance": distance,
            })

        return retrieved_chunks

    def delete_document(self, document_id: str) -> int:
        """Delete all chunks belonging to a document."""

        if not isinstance(document_id, str) or not document_id.strip():
            raise ValueError("document_id must be a non-empty string.")

        existing = self.collection.get(
            where={"document_id": document_id},
            include=[],
        )

        ids = existing.get("ids", [])

        if ids:
            self.collection.delete(ids=ids)

        return len(ids)

    def count(self) -> int:
        """Return the total number of stored chunks."""

        return self.collection.count()
