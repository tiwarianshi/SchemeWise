
import pytest

import services.document_service as document_service


@pytest.fixture
def sample_extraction():
    return {
        "total_pages": 2,
        "extracted_pages": 2,
        "empty_pages": [],
        "pages": [
            {"page_number": 1, "text": "Government scheme eligibility."},
            {"page_number": 2, "text": "Required documents and application."},
        ],
    }


@pytest.fixture
def sample_chunks():
    return [
        {
            "document_id": "doc-123",
            "page_number": 1,
            "chunk_index": 0,
            "page_chunk_index": 0,
            "token_count": 5,
            "text": "Government scheme eligibility.",
        },
        {
            "document_id": "doc-123",
            "page_number": 2,
            "chunk_index": 1,
            "page_chunk_index": 0,
            "token_count": 6,
            "text": "Required documents and application.",
        },
    ]


def test_index_pdf_document_success(
    monkeypatch,
    sample_extraction,
    sample_chunks,
):
    calls = {}

    def fake_extract(pdf_bytes):
        calls["pdf_bytes"] = pdf_bytes
        return sample_extraction

    def fake_chunk(pages, document_id):
        calls["pages"] = pages
        calls["document_id"] = document_id
        return sample_chunks

    def fake_embed(texts):
        calls["texts"] = texts
        return [[0.1] * 768, [0.2] * 768]

    class FakeVectorStore:
        def add_chunks(self, **kwargs):
            calls["stored_data"] = kwargs
            return len(kwargs["chunks"])

    monkeypatch.setattr(
        document_service,
        "extract_pdf_text",
        fake_extract,
    )
    monkeypatch.setattr(
        document_service,
        "chunk_pages",
        fake_chunk,
    )
    monkeypatch.setattr(
        document_service,
        "embed_texts",
        fake_embed,
    )
    monkeypatch.setattr(
        document_service,
        "VectorStoreService",
        FakeVectorStore,
    )

    result = document_service.index_pdf_document(
        pdf_bytes=b"%PDF-test",
        document_id="doc-123",
        scheme_id="scheme-1",
        document_name="Guidelines.pdf",
        source_url="https://example.gov.in/guidelines.pdf",
    )

    assert result == {
        "document_id": "doc-123",
        "document_name": "Guidelines.pdf",
        "scheme_id": "scheme-1",
        "total_pages": 2,
        "extracted_pages": 2,
        "empty_pages": [],
        "total_chunks": 2,
        "stored_chunks": 2,
        "status": "indexed",
    }

    assert calls["pdf_bytes"] == b"%PDF-test"
    assert calls["document_id"] == "doc-123"
    assert len(calls["texts"]) == 2
    assert calls["stored_data"]["scheme_id"] == "scheme-1"
    assert calls["stored_data"]["document_name"] == "Guidelines.pdf"


def test_index_rejects_empty_document_id():
    with pytest.raises(ValueError, match="document_id"):
        document_service.index_pdf_document(
            pdf_bytes=b"%PDF-test",
            document_id="",
        )


def test_index_rejects_when_no_chunks_are_created(
    monkeypatch,
    sample_extraction,
):
    monkeypatch.setattr(
        document_service,
        "extract_pdf_text",
        lambda pdf_bytes: sample_extraction,
    )
    monkeypatch.setattr(
        document_service,
        "chunk_pages",
        lambda pages, document_id: [],
    )

    with pytest.raises(ValueError, match="No text chunks"):
        document_service.index_pdf_document(
            pdf_bytes=b"%PDF-test",
            document_id="doc-123",
        )


def test_index_rejects_embedding_count_mismatch(
    monkeypatch,
    sample_extraction,
    sample_chunks,
):
    monkeypatch.setattr(
        document_service,
        "extract_pdf_text",
        lambda pdf_bytes: sample_extraction,
    )
    monkeypatch.setattr(
        document_service,
        "chunk_pages",
        lambda pages, document_id: sample_chunks,
    )
    monkeypatch.setattr(
        document_service,
        "embed_texts",
        lambda texts: [[0.1] * 768],
    )

    with pytest.raises(RuntimeError, match="Embedding count"):
        document_service.index_pdf_document(
            pdf_bytes=b"%PDF-test",
            document_id="doc-123",
        )


def test_index_propagates_pdf_extraction_error(monkeypatch):
    def fake_extract(pdf_bytes):
        raise ValueError("Invalid PDF file.")

    monkeypatch.setattr(
        document_service,
        "extract_pdf_text",
        fake_extract,
    )

    with pytest.raises(ValueError, match="Invalid PDF"):
        document_service.index_pdf_document(
            pdf_bytes=b"invalid",
            document_id="doc-123",
        )
