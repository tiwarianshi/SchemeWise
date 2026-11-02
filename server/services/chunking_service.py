
import re
from typing import Any

import tiktoken


# Initial chunking configuration
MAX_CHUNK_TOKENS = 700
CHUNK_OVERLAP_TOKENS = 120

# Keep one consistent tokenizer for chunking.
TOKENIZER = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Return the number of tokens in a text string."""
    return len(TOKENIZER.encode(text))


def split_into_sentences(text: str) -> list[str]:
    """
    Split text at sentence and paragraph boundaries.
    Supports common English and Hindi punctuation.
    """
    text = text.strip()

    if not text:
        return []

    parts = re.split(
        r"\n\s*\n|(?<=[.!?।])\s+",
        text,
    )

    return [
        part.strip()
        for part in parts
        if part.strip()
    ]


def split_long_sentence(
    sentence: str,
    max_tokens: int,
) -> list[str]:
    """Split sentences that exceed the token limit."""

    tokens = TOKENIZER.encode(sentence)

    if len(tokens) <= max_tokens:
        return [sentence]

    parts = []

    for start in range(0, len(tokens), max_tokens):
        token_slice = tokens[start:start + max_tokens]
        part = TOKENIZER.decode(token_slice).strip()

        if part:
            parts.append(part)

    return parts


def create_page_chunks(
    text: str,
    max_tokens: int = MAX_CHUNK_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
) -> list[dict[str, Any]]:
    """
    Create overlapping chunks from one PDF page.

    Sentence boundaries are preferred.
    Long sentences are split at token boundaries.
    Actual combined chunk text is checked against max_tokens.
    """

    if max_tokens <= 0:
        raise ValueError("max_tokens must be greater than zero.")

    if overlap_tokens < 0:
        raise ValueError("overlap_tokens cannot be negative.")

    if overlap_tokens >= max_tokens:
        raise ValueError(
            "overlap_tokens must be smaller than max_tokens."
        )

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    # Break unusually long sentences into smaller units.
    units = []

    for sentence in sentences:
        units.extend(
            split_long_sentence(sentence, max_tokens)
        )

    chunks = []
    start = 0

    while start < len(units):
        end = start
        best_text = ""

        # Add units while checking the actual combined text.
        while end < len(units):
            candidate = "\n".join(units[start:end + 1])

            if count_tokens(candidate) > max_tokens:
                break

            best_text = candidate
            end += 1

        # Safety check: every unit must fit individually.
        if end == start:
            raise ValueError(
                "Unable to create a valid token-limited chunk."
            )

        chunks.append({
            "text": best_text,
            "token_count": count_tokens(best_text),
        })

        if end >= len(units):
            break

        # Select whole trailing units for approximate overlap.
        overlap_count = 0
        next_start = end

        for index in range(end - 1, start - 1, -1):
            size = count_tokens(units[index])

            if overlap_count + size > overlap_tokens:
                break

            overlap_count += size
            next_start = index

        # Ensure the loop always makes progress.
        start = next_start if next_start < end else end

    return chunks


def chunk_pages(
    pages: list[dict[str, Any]],
    document_id: str,
    max_tokens: int = MAX_CHUNK_TOKENS,
    overlap_tokens: int = CHUNK_OVERLAP_TOKENS,
) -> list[dict[str, Any]]:
    """
    Create chunks from extracted PDF pages.

    Each chunk retains:
    - document_id
    - original PDF page number
    - global chunk index
    - page-specific chunk index
    - text
    - token count

    Pages are processed independently.
    """

    if not document_id or not document_id.strip():
        raise ValueError("document_id is required.")

    if not isinstance(pages, list):
        raise ValueError("pages must be a list.")

    all_chunks = []
    global_chunk_index = 0

    for page in pages:
        if not isinstance(page, dict):
            raise ValueError("Each page must be a dictionary.")

        page_number = page.get("page_number")
        text = page.get("text", "")

        if (
            not isinstance(page_number, int)
            or isinstance(page_number, bool)
            or page_number < 1
        ):
            raise ValueError(
                "Each page must have a valid page_number."
            )

        if not isinstance(text, str):
            raise ValueError("Page text must be a string.")

        page_chunks = create_page_chunks(
            text=text,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )

        for page_chunk_index, chunk in enumerate(page_chunks):
            all_chunks.append({
                "document_id": document_id,
                "page_number": page_number,
                "chunk_index": global_chunk_index,
                "page_chunk_index": page_chunk_index,
                "text": chunk["text"],
                "token_count": chunk["token_count"],
            })

            global_chunk_index += 1

    return all_chunks
