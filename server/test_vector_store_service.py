
import gc

import pytest

from services.vector_store_service import VectorStoreService


def make_embedding(position=0):
    """Create a predictable 768-dimensional test vector."""
    vector = [0.0] * 768
    vector[position] = 1.0
    return vector


def make_chunk(
    document_id="doc-1",
    page_number=1,
    chunk_index=0,
    text="Government scheme information.",
):
    return {
        "document_id": document_id,
        "page_number": page_number,
        "chunk_index": chunk_index,
        "page_chunk_index": 0,
        "token_count": 10,
        "text": text,
    }


def test_empty_store_returns_zero_and_no_results(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    assert store.count() == 0
    assert store.query_chunks(make_embedding()) == []


def test_add_chunks_and_count(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    chunks = [
        make_chunk(chunk_index=0, text="First chunk"),
        make_chunk(chunk_index=1, page_number=2, text="Second chunk"),
    ]

    added = store.add_chunks(
        chunks,
        [make_embedding(0), make_embedding(1)],
        scheme_id="scheme-1",
        document_name="Guidelines.pdf",
    )

    assert added == 2
    assert store.count() == 2


def test_query_returns_relevant_chunk_and_metadata(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    store.add_chunks(
        [
            make_chunk(
                document_id="doc-1",
                chunk_index=0,
                text="Information about eligibility.",
            ),
            make_chunk(
                document_id="doc-2",
                chunk_index=0,
                text="Information about application documents.",
            ),
        ],
        [make_embedding(0), make_embedding(1)],
    )

    results = store.query_chunks(
        query_embedding=make_embedding(0),
        n_results=2,
    )

    assert len(results) == 2
    assert results[0]["text"] == "Information about eligibility."
    assert results[0]["metadata"]["document_id"] == "doc-1"
    assert results[0]["metadata"]["page_number"] == 1
    assert results[0]["distance"] is not None


def test_query_filters_by_scheme_and_document(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    store.add_chunks(
        [
            make_chunk(document_id="doc-1", text="Scheme one information."),
            make_chunk(document_id="doc-2", text="Scheme two information."),
        ],
        [make_embedding(0), make_embedding(0)],
        scheme_id="scheme-1",
    )

    # Add a document belonging to another scheme.
    store.add_chunks(
        [
            make_chunk(document_id="doc-3", text="Another scheme information.")
        ],
        [make_embedding(0)],
        scheme_id="scheme-2",
    )

    scheme_results = store.query_chunks(
        make_embedding(0),
        scheme_id="scheme-1",
    )

    assert len(scheme_results) == 2
    assert all(
        result["metadata"]["scheme_id"] == "scheme-1"
        for result in scheme_results
    )

    document_results = store.query_chunks(
        make_embedding(0),
        scheme_id="scheme-1",
        document_id="doc-1",
    )

    assert len(document_results) == 1
    assert document_results[0]["metadata"]["document_id"] == "doc-1"


def test_upsert_does_not_create_duplicate_chunks(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    chunk = make_chunk(text="Original information.")

    store.add_chunks([chunk], [make_embedding(0)])
    store.add_chunks(
        [make_chunk(text="Updated information.")],
        [make_embedding(0)],
    )

    assert store.count() == 1

    results = store.query_chunks(make_embedding(0))

    assert len(results) == 1
    assert results[0]["text"] == "Updated information."


def test_delete_document_removes_all_its_chunks(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    store.add_chunks(
        [
            make_chunk(document_id="doc-1", chunk_index=0),
            make_chunk(document_id="doc-1", chunk_index=1),
            make_chunk(document_id="doc-2", chunk_index=0),
        ],
        [
            make_embedding(0),
            make_embedding(1),
            make_embedding(2),
        ],
    )

    deleted = store.delete_document("doc-1")

    assert deleted == 2
    assert store.count() == 1

    results = store.query_chunks(make_embedding(2))

    assert len(results) == 1
    assert results[0]["metadata"]["document_id"] == "doc-2"


def test_data_persists_after_reopening_database(tmp_path):
    db_path = tmp_path / "persistent_chroma"

    store = VectorStoreService(db_path)

    store.add_chunks(
        [make_chunk(text="Persistent government information.")],
        [make_embedding(0)],
    )

    assert store.count() == 1

    # Release the first service before reopening.
    del store
    gc.collect()

    reopened_store = VectorStoreService(db_path)

    assert reopened_store.count() == 1

    results = reopened_store.query_chunks(make_embedding(0))

    assert results[0]["text"] == "Persistent government information."


def test_invalid_embedding_dimension_is_rejected(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    with pytest.raises(ValueError, match="768 dimensions"):
        store.add_chunks(
            [make_chunk()],
            [[0.1, 0.2, 0.3]],
        )


def test_mismatched_chunk_and_embedding_counts_are_rejected(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    with pytest.raises(ValueError, match="must match"):
        store.add_chunks(
            [make_chunk()],
            [],
        )


def test_invalid_query_limit_is_rejected(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    with pytest.raises(ValueError, match="positive integer"):
        store.query_chunks(make_embedding(0), n_results=0)


def test_delete_requires_document_id(tmp_path):
    store = VectorStoreService(tmp_path / "chroma")

    with pytest.raises(ValueError, match="non-empty string"):
        store.delete_document("")
