from app.rag import answer_question


source = "company_policy.txt"
history = []

questions = [
    "How many days of annual leave do employees receive?",
    "How many of those days can be carried forward?",
    "What about sick leave?",
    "Does the document mention a company dress code?",
]

for question in questions:
    print("=" * 70)
    print(f"Question: {question}")

    answer, results = answer_question(
        question=question,
        source=source,
        history=history,
    )

    print(f"Answer: {answer}")

    if results:
        print(f"Best retrieval distance: {results[0][1]:.4f}")

    history.append(
        {
            "role": "user",
            "content": question,
        }
    )

    history.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    print()

    