from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from pytest_postgresql import factories

from src.models import PaymentStates
from src.models import Receipt

schema_file = Path.cwd().parent / Path("src/db/schema/schema.sql")

# Make the test database be populated with the schema per test session run.
test_postgresql_proc = factories.postgresql_proc(
    load=[schema_file]
)

test_database = factories.postgresql("test_postgresql_proc")

@pytest.fixture(name="data")
def receipt_data()-> dict[str, str | int]:
    return  {
        "id": 0,
        "void_id": "string",
        "card_cvv": "string",
        "currency": "string",
        "order_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "refund_id": "string",
        "voided_at": "2026-10-10T15:22:09.215000+00:00",
        "capture_id": "string",
        "created_at": "2026-10-10T15:22:09.215000+00:00",
        "auth_expiry": "2026-10-10T15:22:09.215000+00:00",
        "captured_at": "2026-10-10T15:22:09.215000+00:00",
        "card_number": "string",
        "customer_id": 0,
        "refunded_at": "2026-10-10T15:22:09.215000+00:00",
        "authorize_id": "string",
        "authorized_at": "2026-10-10T15:22:09.215000+00:00",
        "current_state": "pending",
        "amount_in_cents": 0,
        "card_expiry_year": 0,
        "card_expiry_month": 0
}


@pytest.fixture(name="test_receipt")
def receipt_instance() -> Receipt:
    return Receipt(
        id= None,
        order_id=uuid4(),
        customer_id=1,
        amount_in_cents=2929,
        currency="usd",
        card_number="3434",
        card_cvv="321",
        card_expiry_month=4,
        card_expiry_year=1801,
        current_state=PaymentStates.CAPTURED,
        authorize_id=None,
        authorized_at=None,
        auth_expiry=None,
        capture_id=None,
        captured_at=None,
        void_id=None,
        voided_at=None,
        refund_id=None,
        refunded_at=None,
        created_at=datetime.now()
    )

@pytest.fixture(name="idempotency_header")
def idempotency_header() -> dict[str, str]:
    return {"X-Idempotency-Key":"28323232323"}
