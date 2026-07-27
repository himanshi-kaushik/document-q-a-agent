from pathlib import Path

from app.document_loader import load_document
from app.text_chunker import split_text
from app.vector_store import add_chunks, get_vector_store, search_chunks


PROJECT_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = PROJECT_DIR / "sample-documents"

document_paths = [
    SAMPLE_DIR / "company_policy.txt",
    SAMPLE_DIR / "onboarding_guide.pdf",
]

vector_store = get_vector_store()

for document_path in document_paths:
    text = load_document(document_path)
    chunks = split_text(text)

    number_added = add_chunks(
        vector_store=vector_store,
        chunks=chunks,
        source=document_path.name,
    )

    print(f"Stored {number_added} chunks from {document_path.name}")

test_cases = [
    (
        "How many days of annual leave do employees receive?",
        "company_policy.txt",
    ),
    (
        "How many days per week can employees work remotely?",
        "company_policy.txt",
    ),
    (
        "How long is the employee orientation program?",
        "onboarding_guide.pdf",
    ),
    (
        "What is the company dress code?",
        "company_policy.txt",
    ),
]

for question, source in test_cases:
    print("\n" + "#" * 70)
    print(f"Question: {question}")

    results = search_chunks(
    vector_store=vector_store,
    question=question,
    number_of_results=3,
    source=source,
)
    

    for position, (document, distance) in enumerate(results, start=1):
        print("-" * 60)
        print(f"Result {position}")
        print(f"Distance: {distance:.4f}")
        print(f"Source: {document.metadata['source']}")
        print(f"Chunk: {document.metadata['chunk_index']}")
        print(document.page_content)

