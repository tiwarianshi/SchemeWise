
import pytest

import services.embedding_service as embedding_service


class FakeEmbedding:
    def __init__(self, values):
        self.values = values


class FakeResponse:
    def __init__(self, embeddings):
        self.embeddings = embeddings


class FakeModels:
    def embed_content(self, model, contents, config):
        return FakeResponse([
            FakeEmbedding([0.1] * 768)
            for _ in contents
        ])


class FakeClient:
    def __init__(self):
        self.models = FakeModels()


def test_empty_list_returns_empty_list():
    assert embedding_service.embed_texts([]) == []


def test_rejects_non_list_input():
    with pytest.raises(ValueError):
        embedding_service.embed_texts("hello")


def test_rejects_empty_text():
    with pytest.raises(ValueError):
        embedding_service.embed_texts(["hello", "  "])


def test_returns_one_vector_per_text(monkeypatch):
    monkeypatch.setattr(
        embedding_service,
        "_create_client",
        lambda: FakeClient(),
    )

    vectors = embedding_service.embed_texts([
        "What is this scheme?",
        "Who can apply?",
    ])

    assert len(vectors) == 2
    assert len(vectors[0]) == 768
    assert len(vectors[1]) == 768


def test_single_text_embedding(monkeypatch):
    monkeypatch.setattr(
        embedding_service,
        "_create_client",
        lambda: FakeClient(),
    )

    vector = embedding_service.embed_text("Explain this scheme.")

    assert len(vector) == 768


def test_batches_large_input(monkeypatch):
    calls = []

    class TrackingModels:
        def embed_content(self, model, contents, config):
            calls.append(len(contents))
            return FakeResponse([
                FakeEmbedding([0.1] * 768)
                for _ in contents
            ])

    class TrackingClient:
        def __init__(self):
            self.models = TrackingModels()

    monkeypatch.setattr(
        embedding_service,
        "_create_client",
        lambda: TrackingClient(),
    )

    texts = [f"Sample text {i}" for i in range(35)]
    vectors = embedding_service.embed_texts(texts)

    assert len(vectors) == 35
    assert calls == [16, 16, 3]
