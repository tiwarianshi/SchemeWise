
import pymupdf as fitz


# Maximum PDF upload size: 15 MB
MAX_PDF_SIZE_BYTES = 15 * 1024 * 1024


def extract_pdf_text(pdf_bytes: bytes) -> dict:
    """
    Validate a PDF and extract text page by page.

    Page numbers in the result are 1-based,
    just like the page numbers users see in a PDF reader.
    """

    # 1. Check that file data is provided.
    if not pdf_bytes:
        raise ValueError("No PDF file was provided.")

    # 2. Check the maximum file size.
    if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
        raise ValueError("PDF file must not exceed 15 MB.")

    # 3. Check the PDF file signature.
    if not pdf_bytes.startswith(b"%PDF-"):
        raise ValueError("Invalid file. Please upload a valid PDF.")

    # 4. Open and process the PDF.
    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:

            # Reject password-protected PDFs.
            if document.needs_pass:
                raise ValueError(
                    "Password-protected PDFs are not supported."
                )

            # Reject PDFs without pages.
            if document.page_count == 0:
                raise ValueError("The PDF contains no pages.")

            pages = []
            empty_pages = []

            # 5. Extract text from each page.
            for page_index, page in enumerate(document):

                text = page.get_text("text").strip()

                # Convert zero-based index to human page number.
                page_number = page_index + 1

                if text:
                    pages.append({
                        "page_number": page_number,
                        "text": text,
                    })
                else:
                    empty_pages.append(page_number)

            # 6. Reject scanned/image-only PDFs for now.
            if not pages:
                raise ValueError(
                    "No readable text found. "
                    "Scanned PDFs are not supported yet."
                )

            # 7. Return extracted content and metadata.
            return {
                "total_pages": document.page_count,
                "extracted_pages": len(pages),
                "empty_pages": empty_pages,
                "pages": pages,
            }

    except ValueError:
        # Preserve our validation error messages.
        raise

    except Exception as error:
        raise ValueError(
            "Unable to read this PDF. "
            "The file may be corrupted or invalid."
        ) from error
