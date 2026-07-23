from app.llm import get_llm


llm = get_llm()

response = llm.invoke(
    "Reply with exactly these two words: Connection successful"
)

print(response.content)

