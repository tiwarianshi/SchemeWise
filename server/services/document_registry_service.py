
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]

DEFAULT_DB_PATH = SERVER_DIR / "storage" / "documents.db"


class DocumentRegistryService:
    """Stores metadata about uploaded and indexed PDF documents."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH

        self.db_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._initialize_database()

    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize_database(self):
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    document_name TEXT NOT NULL,
                    original_filename TEXT NOT NULL,
                    scheme_id TEXT,
                    source_url TEXT,
                    file_path TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    total_pages INTEGER NOT NULL,
                    extracted_pages INTEGER NOT NULL,
                    total_chunks INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )

    def add_document(self, document: dict) -> dict:
        required_fields = [
            "document_id",
            "document_name",
            "original_filename",
            "file_path",
            "file_size",
            "total_pages",
            "extracted_pages",
            "total_chunks",
            "status",
        ]

        for field in required_fields:
            if field not in document:
                raise ValueError(f"Missing document field: {field}")

        created_at = datetime.now(timezone.utc).isoformat()

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO documents (
                    document_id,
                    document_name,
                    original_filename,
                    scheme_id,
                    source_url,
                    file_path,
                    file_size,
                    total_pages,
                    extracted_pages,
                    total_chunks,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    document["document_id"],
                    document["document_name"],
                    document["original_filename"],
                    document.get("scheme_id"),
                    document.get("source_url"),
                    document["file_path"],
                    document["file_size"],
                    document["total_pages"],
                    document["extracted_pages"],
                    document["total_chunks"],
                    document["status"],
                    created_at,
                ),
            )

        return self.get_document(document["document_id"])

    def get_document(self, document_id: str) -> dict | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?",
                (document_id,),
            ).fetchone()

        return dict(row) if row else None

    def list_documents(self) -> list[dict]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT * FROM documents
                ORDER BY created_at DESC
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def delete_document(self, document_id: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM documents WHERE document_id = ?",
                (document_id,),
            )

        return cursor.rowcount > 0
