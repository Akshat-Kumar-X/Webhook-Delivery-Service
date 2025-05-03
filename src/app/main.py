from fastapi import FastAPI
from .routers import subscriptions

app = FastAPI(title="Webhook Delivery Service")

app.include_router(subscriptions.router)

@app.get("/health", tags=["internal"])
async def health():
    return {"status": "ok"}
