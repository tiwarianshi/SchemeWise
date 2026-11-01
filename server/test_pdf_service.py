
import pymupdf as fitz
import pytest

from services.pdf_service import extract_pdf_text


def create_test_pdf(pages):
    """Create an in-memory PDF for testing."""
    document = fitz.open()

    for page_text in pages:
        page = document.new_page()
        page.insert_text((72, 72), page_text)

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes


def test_extract_valid_pdf():
    pdf_bytes = create_test_pdf([
        "Government Scholarship Guidelines",
        "Annual family income must not exceed Rs. 3,50,000.",
    ])

    result = extract_pdf_text(pdf_bytes)

    assert result["total_pages"] == 2
    assert result["extracted_pages"] == 2
    assert result["pages"][0]["page_number"] == 1
    assert "Scholarship" in result["pages"][0]["text"]
    assert result["pages"][1]["page_number"] == 2


def test_reject_empty_file():
    with pytest.raises(ValueError, match="No PDF file"):
        extract_pdf_text(b"")


def test_reject_non_pdf_file():
    with pytest.raises(ValueError, match="valid PDF"):
        extract_pdf_text(b"This is not a PDF")


def test_reject_oversized_file():
    oversized_pdf = b"%PDF-" + (
        b"x" * (15 * 1024 * 1024)
    )

    with pytest.raises(ValueError, match="15 MB"):
        extract_pdf_text(oversized_pdf)


def test_reject_pdf_without_readable_text():
    pdf_bytes = create_test_pdf(["", ""])

    with pytest.raises(ValueError, match="No readable text"):
        extract_pdf_text(pdf_bytes)


def test_track_empty_pages():
    pdf_bytes = create_test_pdf([
        "First page contains text.",
        "",
        "Third page contains text.",
    ])

    result = extract_pdf_text(pdf_bytes)

    assert result["total_pages"] == 3
    assert result["extracted_pages"] == 2
    assert result["empty_pages"] == [2]


def test_page_numbers_are_one_based():
    pdf_bytes = create_test_pdf([
        "Page one",
        "Page two",
        "Page three",
    ])

    result = extract_pdf_text(pdf_bytes)

    page_numbers = [
        page["page_number"]
        for page in result["pages"]
    ]

    assert page_numbers == [1, 2, 3]
