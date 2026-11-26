from fastapi import FastAPI

app = FastAPI(title="ServiceBay")

@app.get("/health")
def health():
    return {"status": "ok"}
