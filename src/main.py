from src.controllers import query_controller
from src.controllers import document_controller
from controllers import health_controller
from dotenv import load_dotenv
from configs.settings import get_settings
from fastapi import FastAPI

load_dotenv()

settings=get_settings()

app=FastAPI(
    title=settings.app_name
)

app.include_router(health_controller.router)
app.include_router(document_controller.router)
app.include_router(query_controller.router)

@app.get("/")
async def hello()->dict[str, str]:
    return {
        "message": "Welcome to Youtube Transcript RAG"
    }


def main()->None:
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)