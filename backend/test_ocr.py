from pathlib import Path

from app.document_loader import load_document


PROJECT_DIR = Path(__file__).resolve().parent.parent
IMAGE_PATH = PROJECT_DIR / "sample-documents" / "ocr_sample.png"

text = load_document(IMAGE_PATH)

print("Extracted OCR text:")
print("=" * 60)
print(text)
