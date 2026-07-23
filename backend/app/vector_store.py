from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.embeddings import get_embedding_model


BACKEND_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BACKEND_DIR / "chroma_data"
COLLECTION_NAME = "document_chunks"


def get_vector_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embedding_model(),
        persist_directory=str(CHROMA_DIR),
        collection_configuration={"hnsw": {"space": "cosine"}},
    )


def add_chunks(
    vector_store: Chroma,
    chunks: list[str],
    source: str,
) -> int:
    documents = [
        Document(
            page_content=chunk,
            metadata={
                "source": source,
                "chunk_index": index,
            },
        )
        for index, chunk in enumerate(chunks)
    ]

    ids = [
        f"{Path(source).stem}-chunk-{index}"
        for index in range(len(chunks))
    ]

    vector_store.add_documents(documents=documents, ids=ids)

    return len(documents)


def search_chunks(
    vector_store: Chroma,
    question: str,
    number_of_results: int = 3,
    source: str | None = None,
):
    search_filter = {"source": source} if source else None

    return vector_store.similarity_search_with_score(
        question,
        k=number_of_results,
        filter=search_filter,
    )

