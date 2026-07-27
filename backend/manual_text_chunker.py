from pathlib import Path

from app.document_loader import load_document
from app.text_chunker import split_text


PROJECT_DIR = Path(__file__).resolve().parent.parent
DOCUMENT_PATH = PROJECT_DIR / "sample-documents" / "onboarding_guide.pdf"

text = load_document(DOCUMENT_PATH)
chunks = split_text(text)

print(f"Original document characters: {len(text)}")
print(f"Number of chunks created: {len(chunks)}")

for index, chunk in enumerate(chunks, start=1):
    print("=" * 60)
    print(f"Chunk {index} - {len(chunk)} characters")
    print(chunk)
