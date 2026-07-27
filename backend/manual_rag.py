from app.rag import answer_question


test_cases = [
    (
        "How many days of annual leave do employees receive?",
        "company_policy.txt",
    ),
    (
        "How many days per week can employees work remotely?",
        "company_policy.txt",
    ),
    (
        "How long is the employee orientation program?",
        "onboarding_guide.pdf",
    ),
    (
        "What is the company dress code?",
        "company_policy.txt",
    ),
]

for question, source in test_cases:
    print("=" * 70)
    print(f"Document: {source}")
    print(f"Question: {question}")

    answer, results = answer_question(
        question=question,
        source=source,
    )

    print(f"Answer: {answer}")

    if results:
        print(f"Best retrieval distance: {results[0][1]:.4f}")

    print()
    