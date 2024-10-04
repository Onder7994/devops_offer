from typing import Annotated, List, Sequence

from fastapi import APIRouter, Depends, Request, status, Form, HTTPException, Path
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi_users.exceptions import (
    InvalidPasswordException,
    UserNotExists,
)
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.dependencies import get_user_manager, get_user_by_username
from src.auth.manager import UserManager
from src.auth.schemas import UserUpdate
from .schemas import EditProfileForm
from src.category.models import Category
from src.common.dependencies import get_categories
from src.config import settings
from src.auth.fastapi_users import current_active_user_ui
from src.auth.models import User
from src.db.database import db_helper
from src.favorite.dependencies import get_user_favorites, remove_favorite
from starlette.responses import RedirectResponse
from src.utils.utils import get_hashed_password, verify_password

templates = Jinja2Templates(directory="templates")

router = APIRouter(prefix=settings.views.prefix_profile, include_in_schema=False)


@router.get("", response_class=HTMLResponse)
async def profile(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    favorites = await get_user_favorites(user=user, session=session)
    return templates.TemplateResponse(
        "auth/profile.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
            "favorites": favorites,
        },
    )


@router.get("/edit", response_class=HTMLResponse)
async def edit_profile_form(
    request: Request,
    user: Annotated[User, Depends(current_active_user_ui)],
    categories: Sequence[Category] = Depends(get_categories),
):
    if user is None:
        return RedirectResponse(url="/auth/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "auth/edit_profile.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
        },
    )


@router.post("/edit", response_class=HTMLResponse)
async def edit_profile(
    request: Request,
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    user: Annotated[User, Depends(current_active_user_ui)],
    user_manager: Annotated[UserManager, Depends(get_user_manager)],
    categories: Sequence[Category] = Depends(get_categories),
    username: str = Form(...),
    email: str = Form(...),
    change_password: bool = Form(False),
    current_password: str = Form(None),
    new_password: str = Form(None),
):
    errors = []
    try:
        form = EditProfileForm(
            username=username,
            email=email,
            change_password=change_password,
            current_password=current_password,
            new_password=new_password,
        )
    except ValidationError as err:
        errors_messages = [err["msg"] for err in err.errors()]
        return templates.TemplateResponse(
            "auth/edit_profile.html",
            {
                "request": request,
                "errors": errors_messages,
                "categories": categories,
                "user": user,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    if form.email != user.email:
        try:
            is_user_exist = await user_manager.get_by_email(user_email=form.email)
            if is_user_exist:
                errors.append("Пользователь с таким email уже существует")
        except UserNotExists:
            pass

    if form.change_password:
        if not verify_password(form.current_password, user.hashed_password):
            errors.append("Текущий пароль введен неправильно.")

    if form.username != user.username:
        is_user_exist = await get_user_by_username(
            username=form.username, session=session
        )
        if is_user_exist:
            errors.append("Пользователь с таким именем уже зарегистрирован")

    if errors:
        return templates.TemplateResponse(
            "auth/edit_profile.html",
            {
                "request": request,
                "errors": errors,
                "user": user,
                "categories": categories,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user_updated_data = {
            "username": form.username,
            "email": form.email,
        }

        if form.change_password and form.new_password:
            user_updated_data["password"] = form.new_password

        user_update = UserUpdate(**user_updated_data)
        user = await user_manager.update(
            user_update=user_update, user=user, request=request
        )

    except InvalidPasswordException as err:
        return templates.TemplateResponse(
            "auth/edit_profile.html",
            {
                "request": request,
                "errors": [str(err)],
                "categories": categories,
                "user": user,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    except Exception:
        return templates.TemplateResponse(
            "auth/edit_profile.html",
            {
                "request": request,
                "errors": [
                    "Произошла неизвестная ошибка. Пожалуйста, попробуйте позже"
                ],
                "categories": categories,
                "user": user,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return templates.TemplateResponse(
        "auth/edit_profile.html",
        {
            "request": request,
            "user": user,
            "categories": categories,
            "success": True,
        },
        status_code=status.HTTP_200_OK,
    )


@router.get("/delete_favorite/{favorite_id}")
async def delete_from_favorite(
    user: Annotated[User, Depends(current_active_user_ui)],
    session: Annotated[AsyncSession, Depends(db_helper.session_getter)],
    favorite_id: str = Path(...),
):
    if user is None:
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    try:
        favorite_id_int = int(favorite_id)
    except ValueError:
        return RedirectResponse("/profile", status_code=status.HTTP_302_FOUND)
    try:
        await remove_favorite(favorite_id=favorite_id_int, session=session, user=user)
    except (HTTPException, ValidationError):
        return RedirectResponse("/profile", status_code=status.HTTP_303_SEE_OTHER)
    return RedirectResponse("/profile", status_code=status.HTTP_302_FOUND)
