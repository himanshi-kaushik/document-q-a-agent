from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.document_loader import load_document
from app.text_chunker import split_text
from app.vector_store import add_chunks, get_vector_store

from app.rag import answer_question
from app.schemas import AskQuestionRequest, AskQuestionResponse
from app.session_store import (
    add_conversation_turn,
    create_session,
    get_session,
)

app = FastAPI(
    title="Document Q&A Agent API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "Document Q&A Agent API is running."
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

MAX_FILE_SIZE = 10 * 1024 * 1024
SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".png",
    ".jpg",
    ".jpeg",
}


@app.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="A filename is required.",
        )

    extension = Path(file.filename).suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, PNG, JPG, and JPEG files are supported.",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty.",
        )

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="The file must be smaller than 10 MB.",
        )

    temporary_path = None

    try:
        with NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temporary_file:
            temporary_file.write(contents)
            temporary_path = Path(temporary_file.name)

        text = load_document(temporary_path)
        chunks = split_text(text)

        document_id = str(uuid4())
        vector_store = get_vector_store()

        chunks_stored = add_chunks(
            vector_store=vector_store,
            chunks=chunks,
            source=file.filename,
            document_id=document_id,
        )
        session_id = create_session(document_id)

        return {
            "document_id": document_id,
            "session_id": session_id,
            "filename": file.filename,
            "chunks_stored": chunks_stored,
            "message": "Document uploaded and processed successfully.",
        }
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="The document could not be processed.",
        ) from error

    finally:
        await file.close()

        if temporary_path and temporary_path.exists():
            temporary_path.unlink()


@app.post(
    "/questions/ask",
    response_model=AskQuestionResponse,
)
def ask_question(request: AskQuestionRequest):
    session = get_session(request.session_id)

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Conversation session not found. Upload the document again.",
        )

    if session["document_id"] != request.document_id:
        raise HTTPException(
            status_code=400,
            detail="The session does not belong to this document.",
        )

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="The question cannot be empty.",
        )

    try:
        answer, results = answer_question(
            question=question,
            document_id=request.document_id,
            history=session["history"],
        )
    except Exception as error:
        raise HTTPException(
            status_code=503,
            detail="The question could not be answered at this time.",
        ) from error

    add_conversation_turn(
        session_id=request.session_id,
        question=question,
        answer=answer,
    )

    sources = [
        {
            "source": document.metadata.get("source", "unknown"),
            "chunk_index": document.metadata.get("chunk_index", 0),
            "distance": round(float(distance), 4),
        }
        for document, distance in results
    ]

    return {
        "answer": answer,
        "session_id": request.session_id,
        "sources": sources,
    }
