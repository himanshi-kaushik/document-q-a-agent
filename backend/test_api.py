import pytest
from fastapi.testclient import TestClient
from langchain_core.documents import Document

from app import main
from app.session_store import sessions


client = TestClient(main.app)


@pytest.fixture(autouse=True)
def clear_sessions():
    sessions.clear()


@pytest.fixture
def mock_document_pipeline(monkeypatch):
    monkeypatch.setattr(
        main,
        "load_document",
        lambda file_path: "Employees receive 18 days of annual leave.",
    )

    monkeypatch.setattr(
        main,
        "split_text",
        lambda text: [text],
    )

    monkeypatch.setattr(
        main,
        "get_vector_store",
        lambda: object(),
    )

    monkeypatch.setattr(
        main,
        "add_chunks",
        lambda **kwargs: 1,
    )


def upload_test_document():
    return client.post(
        "/documents/upload",
        files={
            "file": (
                "policy.txt",
                b"Sample policy text",
                "text/plain",
            )
        },
    )


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_document_upload(mock_document_pipeline):
    response = upload_test_document()
    data = response.json()

    assert response.status_code == 200
    assert data["filename"] == "policy.txt"
    assert data["chunks_stored"] == 1
    assert data["document_id"]
    assert data["session_id"]


def test_unsupported_file_type():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "malware.exe",
                b"unsupported",
                "application/octet-stream",
            )
        },
    )

    assert response.status_code == 400


def test_question_endpoint(
    mock_document_pipeline,
    monkeypatch,
):
    upload_response = upload_test_document().json()

    retrieved_document = Document(
        page_content="Employees receive 18 days of annual leave.",
        metadata={
            "source": "policy.txt",
            "chunk_index": 0,
        },
    )

    monkeypatch.setattr(
        main,
        "answer_question",
        lambda **kwargs: (
            "Employees receive 18 days of annual leave.",
            [(retrieved_document, 0.25)],
        ),
    )

    response = client.post(
        "/questions/ask",
        json={
            "document_id": upload_response["document_id"],
            "session_id": upload_response["session_id"],
            "question": "How many annual leave days are provided?",
        },
    )

    data = response.json()

    assert response.status_code == 200
    assert data["answer"] == (
        "Employees receive 18 days of annual leave."
    )
    assert data["sources"][0]["source"] == "policy.txt"


def test_invalid_session():
    response = client.post(
        "/questions/ask",
        json={
            "document_id": "document-123",
            "session_id": "invalid-session",
            "question": "What is the leave policy?",
        },
    )

    assert response.status_code == 404
