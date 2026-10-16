from src.core import settings
import httpx

METHOD="POST"

print(settings.BANK_AUTHORIZE_URL)
response = httpx.get(url="http:://127.0.0.1:8787/health")
