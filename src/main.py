from contextlib import asynccontextmanager
from typing import Annotated, Sequence

from fastapi import FastAPI, Request, Depends, status
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from src.category.dependencies import get_all_category
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
from src.auth.views import router as password_reset_view_router
from src.auth.login.views import router as login_view_router
from src.auth.register.views import router as register_view_router
from src.profile.views import router as profile_view_router
from src.admin.views import router as admin_ui_view_router
import uvicorn
from src.config import settings
from src.db.database import db_helper
from src.common.dependencies import get_categories
import logging

logging.basicConfig(format=settings.logging.log_format)

templates = Jinja2Templates(directory="templates")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start
    yield
    # shutdown
    await db_helper.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.run.title,
    default_response_class=ORJSONResponse,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

api_app = FastAPI(
    lifespan=lifespan,
    title=settings.run.title,
    default_response_class=ORJSONResponse,
)

front_app = FastAPI(
    lifespan=lifespan,
    title=settings.run.title,
    default_response_class=ORJSONResponse,
    openapi_url=None,
    docs_url=None,
    redoc_url=None,
)

app.mount("/api", api_app)
app.mount("/", front_app)

api_app.include_router(auth_router)
api_app.include_router(favorite_router)
api_app.include_router(category_router)
api_app.include_router(question_router)
api_app.include_router(answer_router)

front_app.mount("/static", StaticFiles(directory="static"), name="static")
front_app.include_router(category_view_router)
front_app.include_router(question_view_router)
front_app.include_router(login_view_router)
front_app.include_router(register_view_router)
front_app.include_router(password_reset_view_router)
front_app.include_router(profile_view_router)
front_app.include_router(admin_ui_view_router)


@front_app.exception_handler(StarletteHTTPException)
async def front_http_exception(
    request: Request,
    exc: StarletteHTTPException,
):
    render_html = ""
    if exc.status_code == status.HTTP_404_NOT_FOUND:
        render_html = "errors/404.html"
    if exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
        render_html = "errors/500.html"
    if exc.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
        return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)

    session_generator = db_helper.session_getter()
    session = await anext(session_generator)
    user = current_active_user_ui
    try:
        categories = await get_all_category(session=session)
    finally:
        await session_generator.aclose()
    return templates.TemplateResponse(
        render_html,
        {
            "request": request,
            "categories": categories,
            "user": user,
        },
        status_code=exc.status_code,
    )


@front_app.get("/", response_class=HTMLResponse)
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


@front_app.get("/api_doc", response_class=HTMLResponse)
async def api_doc(
    request: Request,
    categories: Annotated[Sequence[Category], Depends(get_categories)],
    user: Annotated[User, Depends(current_active_user_ui)] = None,
):
    return templates.TemplateResponse(
        "api_doc.html",
        {
            "request": request,
            "categories": categories,
            "user": user,
        },
    )


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host=settings.run.host,
        port=settings.run.port,
        workers=settings.run.workers,
    )
