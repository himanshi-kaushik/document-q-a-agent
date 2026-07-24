from uuid import uuid4


sessions: dict[str, dict] = {}


def create_session(document_id: str) -> str:
    session_id = str(uuid4())

    sessions[session_id] = {
        "document_id": document_id,
        "history": [],
    }

    return session_id


def get_session(session_id: str) -> dict | None:
    return sessions.get(session_id)


def add_conversation_turn(
    session_id: str,
    question: str,
    answer: str,
) -> None:
    session = sessions[session_id]

    session["history"].append(
        {
            "role": "user",
            "content": question,
        }
    )

    session["history"].append(
        {
            "role": "assistant",
            "content": answer,
        }
    )
