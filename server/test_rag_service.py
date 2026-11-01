
from services import rag_service


class FakeVectorStore:
    def __init__(self, results):
        self.results = results
        self.received_filters = None

    def query_chunks(
        self,
        query_embedding,
        n_results=5,
        scheme_id=None,
        document_id=None,
    ):
        self.received_filters = {
            "n_results": n_results,
            "scheme_id": scheme_id,
            "document_id": document_id,
        }
        return self.results


class FakeGeminiClient:
    def __init__(
        self,
        answer="The document states that students can apply.",
        answer_status="complete",
    ):
        self.answer = answer
        self.answer_status = answer_status
        self.called = False
        self.received_prompt = None
        self.received_config = None

        class Models:
            pass

        self.models = Models()

        def generate_content(model, contents, config=None):
            import json

            self.called = True
            self.received_prompt = contents
            self.received_config = config

            class Response:
                pass

            response = Response()
            response.text = json.dumps({
                "answer": self.answer,
                "answer_status": self.answer_status,
            })

            return response

        self.models.generate_content = generate_content


def make_chunk(distance=0.30):
    return {
        "id": "document-1:0",
        "text": "Students must submit the application form.",
        "distance": distance,
        "metadata": {
            "document_id": "document-1",
            "document_name": "scheme-guidelines.pdf",
            "page_number": 2,
            "source_url": "https://example.gov.in/guidelines.pdf",
        },
    }


def test_relevant_evidence_generates_answer(monkeypatch):
    monkeypatch.setattr(
        rag_service,
        "embed_text",
        lambda question: [0.1] * 768,
    )

    vector_store = FakeVectorStore([make_chunk()])
    gemini = FakeGeminiClient()

    service = rag_service.RAGService(
        vector_store=vector_store,
        gemini_client=gemini,
    )

    result = service.ask("How can students apply?")

    assert result["insufficient_information"] is False
    assert "students can apply" in result["answer"]
    assert len(result["sources"]) == 1
    assert result["sources"][0]["page_number"] == 2
    assert gemini.called is True


def test_no_relevant_evidence_does_not_call_gemini(monkeypatch):
    monkeypatch.setattr(
        rag_service,
        "embed_text",
        lambda question: [0.1] * 768,
    )

    vector_store = FakeVectorStore([make_chunk(distance=0.90)])
    gemini = FakeGeminiClient()

    service = rag_service.RAGService(
        vector_store=vector_store,
        gemini_client=gemini,
    )

    result = service.ask("What is the application deadline?")

    assert result["insufficient_information"] is True
    assert result["sources"] == []
    assert gemini.called is False


def test_question_filters_are_forwarded(monkeypatch):
    monkeypatch.setattr(
        rag_service,
        "embed_text",
        lambda question: [0.1] * 768,
    )

    vector_store = FakeVectorStore([])
    gemini = FakeGeminiClient()

    service = rag_service.RAGService(
        vector_store=vector_store,
        gemini_client=gemini,
    )

    service.ask(
        "What is the scheme benefit?",
        scheme_id="scheme-123",
        document_id="document-456",
    )

    assert vector_store.received_filters == {
        "n_results": 5,
        "scheme_id": "scheme-123",
        "document_id": "document-456",
    }


def test_empty_question_is_rejected():
    service = rag_service.RAGService(
        vector_store=FakeVectorStore([]),
        gemini_client=FakeGeminiClient(),
    )

    try:
        service.ask("   ")
        assert False, "Expected ValueError"
    except ValueError as error:
        assert "empty" in str(error).lower()


def test_complete_answer_status(monkeypatch):
    monkeypatch.setattr(
        rag_service,
        "embed_text",
        lambda question: [0.1] * 768,
    )

    vector_store = FakeVectorStore([make_chunk()])
    gemini = FakeGeminiClient(answer_status="complete")

    service = rag_service.RAGService(
        vector_store=vector_store,
        gemini_client=gemini,
    )

    result = service.ask("How can students apply?")

    assert result["answer_status"] == "complete"
    assert result["insufficient_information"] is False
    assert len(result["sources"]) == 1


def test_partial_answer_status(monkeypatch):
    monkeypatch.setattr(
        rag_service,
        "embed_text",
        lambda question: [0.1] * 768,
    )

    vector_store = FakeVectorStore([make_chunk()])
    gemini = FakeGeminiClient(
        answer="The document mentions the application form, but not the complete application process.",
        answer_status="partial",
    )

    service = rag_service.RAGService(
        vector_store=vector_store,
        gemini_client=gemini,
    )

    result = service.ask("Explain the complete application process.")

    assert result["answer_status"] == "partial"
    assert result["insufficient_information"] is False
    assert len(result["sources"]) == 1


def test_insufficient_answer_status(monkeypatch):
    monkeypatch.setattr(
        rag_service,
        "embed_text",
        lambda question: [0.1] * 768,
    )

    vector_store = FakeVectorStore([make_chunk()])
    gemini = FakeGeminiClient(
        answer="The provided document does not contain enough information.",
        answer_status="insufficient",
    )

    service = rag_service.RAGService(
        vector_store=vector_store,
        gemini_client=gemini,
    )

    result = service.ask("What is the exact scholarship amount?")

    assert result["answer_status"] == "insufficient"
    assert result["insufficient_information"] is True
    assert len(result["sources"]) == 1
