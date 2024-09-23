from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.answer.router import router as answer_router
from src.category.router import router as category_router
from src.question.router import router as question_router
from src.auth.router import router as auth_router
import uvicorn
from src.config import settings
from src.db.database import db_helper
import src.db.models_import
import logging

logging.basicConfig(
    format=settings.logging.log_format
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(lifespan=lifespan, title=settings.run.title)
main_app.include_router(auth_router)
main_app.include_router(category_router)
main_app.include_router(question_router)
main_app.include_router(answer_router)

if __name__ == "__main__":
    uvicorn.run(
        "src.main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
