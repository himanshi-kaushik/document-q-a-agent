from app.embeddings import get_embedding_model


embedding_model = get_embedding_model()

sample_text = "Employees receive 18 days of annual leave."
embedding = embedding_model.embed_query(sample_text)

print(f"Original text: {sample_text}")
print(f"Embedding dimensions: {len(embedding)}")
print(f"First five values: {embedding[:5]}")
