import asyncio

import math

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
    async def __request(cls, url: str, request_class: BankRequest, response_class: BankResponse, idempotency_key: str):
        async with AsyncClient() as client:
            retries = 0
            while True: 
                try:
                    if is_not_retryable(retries):
                        return BankError(
                            error="max_retry_exceeded", 
                            message="max retry exceeded to bank, please try again later",
                            status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
                    
                    wait_in_milliseconds = int((math.pow(2, retries) - 1) * 100) / 1000 # to milliseconds
                    logger.info(f"Retry in.... {wait_in_milliseconds}, retry_count: {retries}")
                    await asyncio.sleep(wait_in_milliseconds)
                    
                    response = await client.post(url=url, json=request_class.model_dump(), headers={"idempotency-key":idempotency_key})
                    if response.status_code == status.HTTP_200_OK:
                        return response_class(**response.json())
                    
                    if response.status_code >=  status.HTTP_500_INTERNAL_SERVER_ERROR:
                        retries += 1
                        continue
                        
                    return BankError(**response.json(), status_code=response.status_code)
                except httpx2.TransportError:
                    retries += 1
                    continue
                    
    
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
    async def refund(cls, data: BankRefundResponse, idempotency_key: str) -> BankRefundResponse | BankError:
        return await cls.__request(url=refund_url, request_class=data, response_class=BankRefundResponse, idempotency_key=idempotency_key)



