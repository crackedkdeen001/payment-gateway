import asyncio

import math
from uuid import UUID

import httpx2

from src.core import settings, logger
from src.dtos.responses import BankAuthorizeResponse, BankCaptureResponse, BankVoidResponse, BankRefundResponse, BankError
from src.dtos.requests import BankAuthorizeRequest, BankCaptureRequest, BankRefundRequest, BankVoidRequest

from httpx2 import AsyncClient
from fastapi import status

BankRequest = BankAuthorizeRequest | BankCaptureRequest | BankRefundRequest | BankVoidRequest
BankResponse = BankAuthorizeResponse | BankCaptureResponse | BankRefundResponse | BankVoidResponse

auth_url = settings.BANK_API_URL + "/authorizations"
capture_url = settings.BANK_API_URL + "/captures"
void_url = settings.BANK_API_URL + "/voids"
refund_url = settings.BANK_API_URL + "/refunds"


def is_not_retryable(retry_count):
    return retry_count >= settings.MAX_RETRY


class BankService:
    @classmethod
    async def __request(cls, url: str, request_class: BankRequest, response_class: BankResponse, idempotency_key: UUID):
        async with AsyncClient() as client:
            for attempts in range(1, settings.MAX_RETRY + 1):
                try:
                    wait_in_milliseconds = int((math.pow(2, attempts - 1) - 1) * 100) / 1000 # to milliseconds
                    logger.info(f"Request Made to the Bank in.... {wait_in_milliseconds}, retry_count: {attempts}")
                    await asyncio.sleep(wait_in_milliseconds)
                    
                    response = await client.post(url=url, json=request_class.model_dump(), headers={"idempotency-key":str(idempotency_key)}, timeout=100)
                    if response.status_code == status.HTTP_200_OK:
                        return response_class(**response.json())
                    
                    if response.status_code >=  status.HTTP_500_INTERNAL_SERVER_ERROR:
                        continue
                        
                    return BankError(**response.json(), status_code=response.status_code)
                except httpx2.TransportError:
                    if attempts == 3:
                        break
                    continue

        return BankError(
            error="max_retry_exceeded",
            message="Max retry exceeded to bank, please try again later",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE)

    
    @classmethod
    async def authorize(cls, data: BankAuthorizeRequest, idempotency_key: str) -> BankAuthorizeResponse | BankError:
        return await cls.__request(url=auth_url, request_class=data, response_class=BankAuthorizeResponse, idempotency_key=idempotency_key)

    @classmethod
    async def capture(cls, data: BankCaptureRequest, idempotency_key: str) -> BankCaptureResponse | BankError:
        return await cls.__request(url=capture_url, request_class=data, response_class=BankCaptureResponse,idempotency_key=idempotency_key)

    @classmethod
    async def void(cls, data: BankVoidRequest, idempotency_key: str) -> BankVoidResponse | BankError:
        return await cls.__request(url=void_url, request_class=data, response_class=BankVoidResponse, idempotency_key=idempotency_key)

    @classmethod
    async def refund(cls, data: BankRefundRequest, idempotency_key: str) -> BankRefundResponse | BankError:
        return await cls.__request(url=refund_url, request_class=data, response_class=BankRefundResponse, idempotency_key=idempotency_key)



