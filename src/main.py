from fastapi import FastAPI

app=FastAPI()

@app.get("/")
async def hello()->dict[str, str]:
    return {
        "message": "Welcome to Youtube Transcript RAG"
    }


def main()->None:
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)