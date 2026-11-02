
from services.pdf_service import extract_pdf_text
from services.chunking_service import chunk_pages
from services.embedding_service import embed_texts
from services.vector_store_service import VectorStoreService


def index_pdf_document(
    pdf_bytes: bytes,
    document_id: str,
    scheme_id: str | None = None,
    document_name: str | None = None,
    source_url: str | None = None,
) -> dict:
    """
    Extract, chunk, embed, and store a government PDF.

    document_id must be unique for each uploaded document.
    """

    if not isinstance(document_id, str) or not document_id.strip():
        raise ValueError("document_id must be a non-empty string.")

    # Step 1: Extract text page by page from the PDF.
    extraction = extract_pdf_text(pdf_bytes)

    # Step 2: Split extracted pages into searchable chunks.
    chunks = chunk_pages(
        pages=extraction["pages"],
        document_id=document_id,
    )

    if not chunks:
        raise ValueError("No text chunks were created from this PDF.")

    # Step 3: Generate Gemini embeddings for every chunk.
    texts = [chunk["text"] for chunk in chunks]
    embeddings = embed_texts(texts)

    if len(embeddings) != len(chunks):
        raise RuntimeError(
            "Embedding count does not match the number of chunks."
        )

    # Step 4: Save chunks and embeddings in persistent ChromaDB.
    vector_store = VectorStoreService()

    stored_count = vector_store.add_chunks(
        chunks=chunks,
        embeddings=embeddings,
        scheme_id=scheme_id,
        document_name=document_name,
        source_url=source_url,
    )

    # Step 5: Return indexing information.
    return {
        "document_id": document_id,
        "document_name": document_name,
        "scheme_id": scheme_id,
        "total_pages": extraction["total_pages"],
        "extracted_pages": extraction["extracted_pages"],
        "empty_pages": extraction["empty_pages"],
        "total_chunks": len(chunks),
        "stored_chunks": stored_count,
        "status": "indexed",
    }
