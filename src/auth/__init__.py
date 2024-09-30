from fastapi import APIRouter
from src.config import settings


__all__ = ["User"]

from .models import User

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_auth, include_in_schema=False)