from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.document_loader import load_document
from app.text_chunker import split_text
from app.vector_store import add_chunks, get_vector_store


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
SUPPORTED_EXTENSIONS = {".pdf", ".txt"}


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
            detail="Only PDF and TXT files are supported.",
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

        return {
            "document_id": document_id,
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

