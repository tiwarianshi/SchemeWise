
import pytest

from services.document_registry_service import DocumentRegistryService


@pytest.fixture
def registry(tmp_path):
    return DocumentRegistryService(tmp_path / "test_documents.db")


def sample_document(document_id="doc-123"):
    return {
        "document_id": document_id,
        "document_name": "Government Guidelines",
        "original_filename": "guidelines.pdf",
        "scheme_id": "scheme-1",
        "source_url": "https://example.gov.in/guidelines.pdf",
        "file_path": "storage/uploads/doc-123.pdf",
        "file_size": 1024,
        "total_pages": 10,
        "extracted_pages": 9,
        "total_chunks": 15,
        "status": "indexed",
    }


def test_add_and_get_document(registry):
    added = registry.add_document(sample_document())

    assert added["document_id"] == "doc-123"
    assert added["document_name"] == "Government Guidelines"
    assert added["status"] == "indexed"
    assert added["file_size"] == 1024
    assert added["scheme_id"] == "scheme-1"

    fetched = registry.get_document("doc-123")

    assert fetched == added


def test_list_documents(registry):
    registry.add_document(sample_document("doc-1"))
    registry.add_document(sample_document("doc-2"))

    documents = registry.list_documents()

    assert len(documents) == 2
    assert {doc["document_id"] for doc in documents} == {
        "doc-1",
        "doc-2",
    }


def test_get_missing_document_returns_none(registry):
    assert registry.get_document("missing-id") is None


def test_delete_document(registry):
    registry.add_document(sample_document())

    assert registry.delete_document("doc-123") is True
    assert registry.get_document("doc-123") is None


def test_delete_missing_document_returns_false(registry):
    assert registry.delete_document("missing-id") is False


def test_duplicate_document_id_is_rejected(registry):
    registry.add_document(sample_document())

    with pytest.raises(Exception):
        registry.add_document(sample_document())


def test_missing_required_field_is_rejected(registry):
    document = sample_document()
    del document["file_path"]

    with pytest.raises(ValueError, match="file_path"):
        registry.add_document(document)


def test_database_persists_after_reopening(tmp_path):
    db_path = tmp_path / "persistent_documents.db"

    first_registry = DocumentRegistryService(db_path)
    first_registry.add_document(sample_document())

    second_registry = DocumentRegistryService(db_path)

    assert second_registry.get_document("doc-123") is not None
