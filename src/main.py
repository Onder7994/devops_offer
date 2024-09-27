from contextlib import asynccontextmanager
from typing import Annotated, Sequence

from fastapi import FastAPI, Request, Depends
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.auth.fastapi_users import current_active_user_ui
from src.category.models import Category
from src.auth.models import User
from src.answer.router import router as answer_router
from src.category.router import router as category_router
from src.category.views import router as category_view_router
from src.question.router import router as question_router
from src.auth.router import router as auth_router
from src.favorite.router import router as favorite_router
from src.question.views import router as question_view_router
from src.auth.views import router as auth_view_router
from src.profile.views import router as profile_view_router
import uvicorn
from src.config import settings
from src.db.database import db_helper
from src.common.dependencies import get_categories
import src.db.models_import
import logging

logging.basicConfig(format=settings.logging.log_format)

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start
    yield
    # shutdown
    await db_helper.dispose()


main_app = FastAPI(
    lifespan=lifespan,
    title=settings.run.title,
    default_response_class=ORJSONResponse,
)
main_app.mount("/static", StaticFiles(directory="static"), name="static")
main_app.include_router(auth_router)
main_app.include_router(favorite_router)
main_app.include_router(category_router)
main_app.include_router(question_router)
main_app.include_router(answer_router)
main_app.include_router(category_view_router)
main_app.include_router(question_view_router)
main_app.include_router(auth_view_router)
main_app.include_router(profile_view_router)


@main_app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home(
    request: Request,
    categories: Annotated[Sequence[Category], Depends(get_categories)],
    user: Annotated[User, Depends(current_active_user_ui)] = None,
):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "categories": categories,
            "user": user,
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
