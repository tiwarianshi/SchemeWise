
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load the .env file located inside the server folder.
SERVER_DIR = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=SERVER_DIR / ".env")

# Gemini embedding configuration.
EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768

# Keep requests in manageable batches.
EMBEDDING_BATCH_SIZE = 16


def _create_client():
    """Create a Gemini client using the API key from server/.env."""

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to server/.env."
        )

    return genai.Client(api_key=api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Convert multiple text chunks into Gemini embedding vectors.

    Returns one 768-dimensional vector for each input text.
    """

    if not isinstance(texts, list):
        raise ValueError("texts must be a list of strings.")

    if not texts:
        return []

    for index, text in enumerate(texts):
        if not isinstance(text, str) or not text.strip():
            raise ValueError(
                f"Text at index {index} must be a non-empty string."
            )

    client = _create_client()
    all_vectors = []

    for start in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[start:start + EMBEDDING_BATCH_SIZE]

        response = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=[
              types.Content(
              parts=[types.Part(text=text)]
               )
               for text in batch
            ],
            config=types.EmbedContentConfig(
                output_dimensionality=EMBEDDING_DIMENSIONS
            ),
        )

        embeddings = response.embeddings or []

        if len(embeddings) != len(batch):
            raise RuntimeError(
                "Gemini returned an unexpected number of embeddings."
            )

        for embedding in embeddings:
            if not embedding.values:
                raise RuntimeError(
                    "Gemini returned an empty embedding vector."
                )

            vector = [float(value) for value in embedding.values]

            if len(vector) != EMBEDDING_DIMENSIONS:
                raise RuntimeError(
                    "Gemini returned an embedding with an unexpected "
                    "number of dimensions."
                )

            all_vectors.append(vector)

    return all_vectors


def embed_text(text: str) -> list[float]:
    """Convert one question or text chunk into an embedding vector."""

    vectors = embed_texts([text])
    return vectors[0]
