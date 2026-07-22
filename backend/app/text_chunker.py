from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 900
CHUNK_OVERLAP = 120

#chunking function
def split_text(text: str) -> list[str]:
    if not text or not text.strip():
        raise ValueError("Cannot split empty text.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_text(text)

