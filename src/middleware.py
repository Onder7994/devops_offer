from fastapi import Request
from typing import Sequence, Optional
from src.category.models import Category
from src.auth.models import User
from src.common.dependencies import get_categories
from src.auth.fastapi_users import current_active_user_ui
