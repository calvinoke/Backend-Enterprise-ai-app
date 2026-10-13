
import asyncio

from app.embeddings.providers.gemini_embedding import (
    GeminiEmbeddingProvider,
)


async def main():
    provider = GeminiEmbeddingProvider()

    print("Provider:", provider.provider_name)
    print("Model:", provider.model_name)
    print("Expected dimensions:", provider.dimension)

    vector = await provider.embed(
        "Enterprise AI Platform document search"
    )
    print("Single vector dimensions:", len(vector))
    assert len(vector) == 768

    vectors = await provider.embed_batch([
        "Authentication and authorization",
        "Semantic search using embeddings",
    ])

    print("Batch size:", len(vectors))
    print("Batch dimensions:", [len(v) for v in vectors])

    assert len(vectors) == 2
    assert all(len(v) == 768 for v in vectors)

    print("PASS: Gemini embedding tests succeeded.")


if __name__ == "__main__":
    asyncio.run(main())
