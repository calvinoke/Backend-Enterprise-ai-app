import asyncio

from app.embeddings.providers.huggingface_embedding import (
    HuggingFaceEmbeddingProvider,
)


async def main():
    provider = HuggingFaceEmbeddingProvider()

    print("Provider:", provider.provider_name)
    print("Model:", provider.model_name)
    print("Expected dimension:", provider.dimension)

    vector = await provider.embed(
        "Enterprise AI Platform document search"
    )

    print("Single vector dimension:", len(vector))
    assert len(vector) == 384

    vectors = await provider.embed_batch(
        [
            "Authentication and authorization",
            "Semantic search using document embeddings",
        ]
    )

    print("Batch size:", len(vectors))
    print("Batch dimensions:", [len(v) for v in vectors])

    assert len(vectors) == 2
    assert all(len(v) == 384 for v in vectors)

    print("PASS: Hosted embedding tests succeeded.")


if __name__ == "__main__":
    asyncio.run(main())