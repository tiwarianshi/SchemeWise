
import pytest

from services.chunking_service import (
    chunk_pages,
    count_tokens,
    create_page_chunks,
)


def test_empty_text_returns_no_chunks():
    assert create_page_chunks("") == []


def test_chunks_respect_token_limit():
    text = "This is a sample sentence. " * 500

    chunks = create_page_chunks(
        text,
        max_tokens=100,
        overlap_tokens=20,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert count_tokens(chunk["text"]) <= 100


def test_chunks_preserve_page_numbers():
    pages = [
        {"page_number": 1, "text": "First page content. " * 100},
        {"page_number": 2, "text": "Second page content. " * 100},
    ]

    chunks = chunk_pages(pages, document_id="doc-1")

    assert chunks
    assert all(chunk["document_id"] == "doc-1" for chunk in chunks)
    assert {chunk["page_number"] for chunk in chunks} == {1, 2}


def test_chunks_do_not_mix_pages():
    pages = [
        {"page_number": 1, "text": "Page one sentence. " * 100},
        {"page_number": 2, "text": "Page two sentence. " * 100},
    ]

    chunks = chunk_pages(pages, document_id="doc-2")

    for chunk in chunks:
        if chunk["page_number"] == 1:
            assert "Page two" not in chunk["text"]
        else:
            assert "Page one" not in chunk["text"]


def test_document_id_is_required():
    with pytest.raises(ValueError):
        chunk_pages(
            [{"page_number": 1, "text": "Some text."}],
            document_id="",
        )


def test_long_sentence_is_split():
    text = "government " * 500

    chunks = create_page_chunks(
        text,
        max_tokens=100,
        overlap_tokens=20,
    )

    assert len(chunks) > 1

    for chunk in chunks:
        assert count_tokens(chunk["text"]) <= 100


def test_hindi_text_is_supported():
    text = "सरकार विद्यार्थियों को छात्रवृत्ति प्रदान करती है। " * 100

    chunks = create_page_chunks(
        text,
        max_tokens=100,
        overlap_tokens=20,
    )

    assert chunks

    for chunk in chunks:
        assert count_tokens(chunk["text"]) <= 100


def test_invalid_overlap_is_rejected():
    with pytest.raises(ValueError):
        create_page_chunks(
            "Some text.",
            max_tokens=100,
            overlap_tokens=100,
        )
