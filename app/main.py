from fastapi import FastAPI

app = FastAPI(
    title="Enterprise AI Platform",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {
        "message": "Enterprise AI Platform API"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }