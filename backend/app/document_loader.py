from pathlib import Path
import fitz #access PyMuPDF

#txt reading function

def load_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8").strip()

#pdf reading function

def load_pdf(file_path: Path) -> str:
    pages = []

    with fitz.open(file_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            if text:
                pages.append(f"[Page {page_number}]\n{text}")

    return "\n\n".join(pages).strip()

#main loader function

def load_document(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    if path.suffix.lower() == ".txt":
        text = load_txt(path)
    elif path.suffix.lower() == ".pdf":
        text = load_pdf(path)
    else:
        raise ValueError("Only PDF and TXT documents are supported.")

    if not text:
        raise ValueError(
            "No readable text was found. The document may be empty or image-only."
        )

    return text



