
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from services.pdf_service import MAX_PDF_SIZE_BYTES
from services.document_service import index_pdf_document
from services.vector_store_service import VectorStoreService
from services.document_registry_service import DocumentRegistryService


router = APIRouter(
    prefix="/api/documents",
    tags=["Documents"],
)

SERVER_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = SERVER_DIR / "storage" / "uploads"


def get_registry():
    return DocumentRegistryService()


def get_vector_store():
    return VectorStoreService()


def public_document(document: dict) -> dict:
    """Hide internal server storage paths from API responses."""
    return {
        key: value
        for key, value in document.items()
        if key != "file_path"
    }


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    scheme_id: str | None = Form(default=None),
):
    # 1. Validate the uploaded filename.
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A PDF filename is required.",
        )

    safe_filename = Path(
        file.filename.replace("\\", "/")
    ).name

    if not safe_filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    # 2. Read at most 15 MB + 1 byte.
    pdf_bytes = file.file.read(MAX_PDF_SIZE_BYTES + 1)

    if not pdf_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(pdf_bytes) > MAX_PDF_SIZE_BYTES:
        raise HTTPException(
            status_code=413,
            detail="PDF file must not exceed 15 MB.",
        )

    # 3. Generate a unique ID and save the PDF.
    document_id = str(uuid4())

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    saved_path = UPLOAD_DIR / f"{document_id}.pdf"

    try:
        saved_path.write_bytes(pdf_bytes)

        # 4. Extract text, create chunks, generate embeddings,
        #    and store the chunks in ChromaDB.
        indexing_result = index_pdf_document(
            pdf_bytes=pdf_bytes,
            document_id=document_id,
            scheme_id=scheme_id,
            document_name=safe_filename,
        )

        # 5. Save document metadata in SQLite.
        registry = get_registry()

        document = registry.add_document({
            "document_id": document_id,
            "document_name": safe_filename,
            "original_filename": safe_filename,
            "scheme_id": scheme_id,
            "source_url": None,
            "file_path": str(saved_path),
            "file_size": len(pdf_bytes),
            "total_pages": indexing_result["total_pages"],
            "extracted_pages": indexing_result["extracted_pages"],
            "total_chunks": indexing_result["stored_chunks"],
            "status": "indexed",
        })

        return {
            "message": "PDF uploaded and indexed successfully.",
            "document": public_document(document),
        }

    except ValueError as error:
        # Invalid or unreadable PDF.
        get_vector_store().delete_document(document_id)

        if saved_path.exists():
            saved_path.unlink()

        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        # Clean up if embedding, storage, or registry fails.
        try:
            get_vector_store().delete_document(document_id)
        except Exception:
            pass

        if saved_path.exists():
            saved_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Unable to process the uploaded PDF.",
        ) from error


@router.get("")
def list_documents():
    documents = get_registry().list_documents()

    return {
        "count": len(documents),
        "documents": [
            public_document(document)
            for document in documents
        ],
    }


@router.get("/{document_id}")
def get_document(document_id: str):
    document = get_registry().get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return public_document(document)


@router.delete("/{document_id}")
def delete_document(document_id: str):
    registry = get_registry()

    document = registry.get_document(document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    # Remove indexed chunks from ChromaDB.
    get_vector_store().delete_document(document_id)

    # Remove the uploaded PDF from local storage.
    saved_path = Path(document["file_path"])

    if saved_path.exists():
        saved_path.unlink()

    # Remove document metadata from SQLite.
    registry.delete_document(document_id)

    return {
        "message": "Document deleted successfully.",
        "document_id": document_id,
    }
