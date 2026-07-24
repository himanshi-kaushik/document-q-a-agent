from langchain_core.prompts import ChatPromptTemplate

from app.llm import get_llm
from app.vector_store import get_vector_store, search_chunks


FALLBACK_RESPONSE = (
    "The information is not available in the provided document."
)

MAX_DISTANCE = 0.65

SYSTEM_PROMPT = """
You are a document question-answering assistant.

Follow these rules:
1. Answer using only the supplied document context.
2. Use conversation history only to understand follow-up references.
3. Do not treat conversation history as factual document evidence.
4. Do not use outside knowledge or make assumptions.
5. If the document context does not contain the answer, respond exactly with:
   The information is not available in the provided document.
6. Keep the answer concise and factual.
""".strip()


prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            """
Conversation history:
{history}

Document context:
{context}

Current question:
{question}
""".strip(),
        ),
    ]
)


def format_context(results) -> str:
    sections = []

    for document, distance in results:
        source = document.metadata.get("source", "unknown")
        chunk_index = document.metadata.get("chunk_index", "unknown")

        sections.append(
            f"[Source: {source}, Chunk: {chunk_index}]\n"
            f"{document.page_content}"
        )

    return "\n\n".join(sections)


def format_history(history: list[dict[str, str]]) -> str:
    if not history:
        return "No previous conversation."

    recent_messages = history[-6:]

    return "\n".join(
        f"{message['role']}: {message['content']}"
        for message in recent_messages
    )


def build_retrieval_question(
    question: str,
    history: list[dict[str, str]],
) -> str:
    if not history:
        return question

    recent_history = format_history(history[-4:])

    return (
        f"Previous conversation:\n{recent_history}\n\n"
        f"Follow-up question:\n{question}"
    )


def answer_question(
    question: str,
    document_id: str | None = None,
    source: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> tuple[str, list]:
    if not document_id and not source:
        raise ValueError(
            "Either document_id or source must be provided."
        )

    history = history or []

    retrieval_question = build_retrieval_question(
        question=question,
        history=history,
    )

    vector_store = get_vector_store()

    results = search_chunks(
    vector_store=vector_store,
    question=retrieval_question,
    number_of_results=3,
    document_id=document_id,
    source=source,
)

    if not results:
        return FALLBACK_RESPONSE, []

    best_distance = results[0][1]

    if best_distance > MAX_DISTANCE:
        return FALLBACK_RESPONSE, results

    context = format_context(results)

    chain = prompt_template | get_llm()

    response = chain.invoke(
        {
            "history": format_history(history),
            "context": context,
            "question": question,
        }
    )

    answer = response.content.strip()

    if not answer:
        answer = FALLBACK_RESPONSE

    return answer, results

