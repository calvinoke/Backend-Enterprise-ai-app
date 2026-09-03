import asyncio
import httpx


async def main():
    # Increased timeout to 5 minutes for model loading
    timeout = httpx.Timeout(300.0, connect=30.0)
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        print("⏳ Sending embedding request... (this may take a while for first load)")
        
        response = await client.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": "Enterprise AI RAG system",
            },
        )
        
        data = response.json()
        print(f" Embedding dimension: {len(data['embedding'])}")


if __name__ == "__main__":
    asyncio.run(main())