from itsdangerous import URLSafeTimedSerializer

# from starlette.requests import Request
from fastapi import Request
from src.config import settings


def generate_csrf_token(request: Request) -> str:
    serializer = URLSafeTimedSerializer(settings.csrf.secret_key)
    csrf_token = serializer.dumps(request.client.host)
    return csrf_token


def validate_csrf_token(request: Request, token: str) -> bool:
    serializer = URLSafeTimedSerializer(settings.csrf.secret_key)
    try:
        token_data = serializer.loads(token, max_age=3600)
    except Exception:
        return False
    return token_data == request.client.host
