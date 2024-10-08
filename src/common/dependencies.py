from typing import Sequence, Any, Tuple, Dict, Callable

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, Request, Response
from src.category.dependencies import get_all_category
from src.question.dependencies import get_all_question
from src.db.database import db_helper


async def get_categories(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Sequence:
    return await get_all_category(session=session)


async def get_all_questions(
    session: AsyncSession = Depends(db_helper.session_getter),
) -> Sequence:
    return await get_all_question(session=session)


def custom_cache_key_builder(
    func,
    namespace: str = "",
    *,
    request: Request = None,
    response: Response = None,
    args: Tuple[Any, ...],
    kwargs: Dict[str, Any],
) -> str:
    return ":".join(
        [
            namespace,
            request.method.lower(),
            request.url.path,
            repr(sorted(request.query_params.items())),
        ]
    )
