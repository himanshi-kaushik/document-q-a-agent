import os
from pathlib import Path

import fitz
import pytesseract
from dotenv import load_dotenv
from PIL import Image


BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")

tesseract_command = os.getenv("TESSERACT_CMD")

if tesseract_command:
    pytesseract.pytesseract.tesseract_cmd = tesseract_command


def extract_text_from_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(
        image,
        lang="eng",
    ).strip()


def load_txt(file_path: Path) -> str:
    return file_path.read_text(encoding="utf-8").strip()


def load_image(file_path: Path) -> str:
    with Image.open(file_path) as image:
        return extract_text_from_image(image.convert("RGB"))


def load_pdf(file_path: Path) -> str:
    pages = []

    with fitz.open(file_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text").strip()

            # Use OCR when the PDF page has no selectable text.
            if not text:
                pixmap = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False,
                )

                image = Image.frombytes(
                    "RGB",
                    (pixmap.width, pixmap.height),
                    pixmap.samples,
                )

                text = extract_text_from_image(image)

            if text:
                pages.append(f"[Page {page_number}]\n{text}")

    return "\n\n".join(pages).strip()


def load_document(file_path: str | Path) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    extension = path.suffix.lower()

    if extension == ".txt":
        text = load_txt(path)
    elif extension == ".pdf":
        text = load_pdf(path)
    elif extension in {".png", ".jpg", ".jpeg"}:
        text = load_image(path)
    else:
        raise ValueError(
            "Only PDF, TXT, PNG, JPG, and JPEG files are supported."
        )

    if not text:
        raise ValueError(
            "No readable text was found in the document."
        )

    return text



