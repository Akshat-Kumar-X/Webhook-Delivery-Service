from fastapi import FastAPI
from .routers import subscriptions, ingest, status

app = FastAPI(title="Webhook Delivery Service")


app.include_router(subscriptions.router)
app.include_router(ingest.router)
app.include_router(status.router)

@app.get("/health", tags=["internal"])
async def health():
    return {"status": "ok"}
