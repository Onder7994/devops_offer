from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from src.config import settings

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_auth, include_in_schema=False)


@router.get("/login", response_class=HTMLResponse, response_model=None)
async def login_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "auth/login.html",
        {
            "request": request,
        },
    )


@router.post("/login", response_class=HTMLResponse, response_model=None)
async def login(request: Request):
    pass


@router.get("/register", response_class=HTMLResponse, response_model=None)
async def register_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "auth/register.html",
        {
            "request": request,
        },
    )


@router.post("/register", response_class=HTMLResponse, response_model=None)
async def register(request: Request):
    pass
