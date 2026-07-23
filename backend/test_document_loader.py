#temporary test code, reads sample documents, number of extracted character and prints first 500 char

from pathlib import Path

from app.document_loader import load_document


PROJECT_DIR = Path(__file__).resolve().parent.parent
SAMPLE_DIR = PROJECT_DIR / "sample-documents"

documents = [
    SAMPLE_DIR / "company_policy.txt",
    SAMPLE_DIR / "onboarding_guide.pdf",
]

for document_path in documents:
    print("=" * 60)
    print(f"Reading: {document_path.name}")

    text = load_document(document_path)

    print(f"Characters extracted: {len(text)}")
    print(text[:500])
    print()
