from time import clock_settime
from typing import Any
from uuid import uuid4

from src.core import settings
from src.dtos.responses import BankAuthorizeResponse, BankCaptureResponse, BankVoidResponse, BankRefundResponse, BankError
from src.dtos.requests import BankAuthorizeRequest, BankCaptureRequest, BankRefundRequest, BankVoidRequest

from httpx import AsyncClient
from fastapi import status

BankRequest = BankAuthorizeRequest | BankCaptureRequest | BankRefundRequest | BankVoidRequest
BankResponse = BankAuthorizeResponse | BankCaptureResponse | BankRefundResponse | BankVoidResponse

auth_url = settings.BANK_API_URL + "/authorizations"
capture_url = settings.BANK_API_URL + "/captures"
void_url = settings.BANK_API_URL + "/voids"
refund_url = settings.BANK_API_URL + "/refunds"


def generate_idempotency_key_header():
    return {"idempotency-key":str(uuid4())}

class BankService:
    @classmethod
    async def __request(cls, url: str, request_class: BankRequest, response_class: BankResponse):
        async with AsyncClient() as client:
            response = await client.post(url=url, json=request_class.model_dump(), headers=generate_idempotency_key_header())
            
            if response.status_code == status.HTTP_200_OK:
                return response_class(**response.json())

            return BankError(**response.json(), status_code=response.status_code)
    
    @classmethod
    async def authorize(cls, data: BankAuthorizeRequest) -> BankAuthorizeResponse | BankError:
        return await cls.__request(url=auth_url, request_class=data, response_class=BankAuthorizeResponse)

    @classmethod
    async def capture(cls, data: BankCaptureRequest) -> BankCaptureResponse | BankError:
        return await cls.__request(url=capture_url, request_class=data, response_class=BankCaptureResponse)

    @classmethod
    async def void(cls, data: BankVoidRequest) -> BankVoidResponse | BankError:
        return await cls.__request(url=void_url, request_class=data, response_class=BankVoidResponse)

    @classmethod
    async def refund(cls, data: BankRefundResponse) -> BankRefundResponse | BankError:
        return await cls.__request(url=refund_url, request_class=data, response_class=BankRefundResponse)
