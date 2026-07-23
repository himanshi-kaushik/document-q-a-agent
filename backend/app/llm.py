import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

DEFAULT_MODEL = "google/gemma-4-26b-a4b-it:free"


def get_llm(model_name: str | None = None) -> ChatOpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is missing from the .env file.")

    selected_model = (
        model_name
        or os.getenv("OPENROUTER_MODEL")
        or DEFAULT_MODEL
    )

    return ChatOpenAI(
        model=selected_model,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=0, #makes answer more consistent and less creative
        max_tokens=300,
        timeout=60,
        max_retries=2,
        default_headers={
            "HTTP-Referer": "http://localhost:5173",
            "X-OpenRouter-Title": "Document Q&A Agent",
        },
    )