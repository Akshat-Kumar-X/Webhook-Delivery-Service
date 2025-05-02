from fastapi import FastAPI

app = FastAPI(title="Webhook Delivery Service")

@app.get("/health", tags=["internal"])
async def health():
    return {"status": "ok"}
