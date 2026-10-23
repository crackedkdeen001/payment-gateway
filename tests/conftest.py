from datetime import datetime
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from pytest_postgresql import factories

from src.db import get_dsn
from src.repository import ReceiptRepository

from src.models import PaymentStates
from src.models import Receipt

schema_file = Path(__file__).resolve().parents[1] / "src/db/schema/schema.sql"

# Make the test database be populated with the schema per test session run.
test_postgresql_proc = factories.postgresql_proc(
    load=[schema_file]
)

test_database = factories.postgresql("test_postgresql_proc")

@pytest.fixture(name="data")
def auth_receipt_data()-> dict[str, str | int]:
    return  {
        "order_id": "orx_f9d2bffc-b23a-4dec-b8c2-d626ce234f54",
        "customer_id": "cux_1",
        "card_number": "stringstrings",
        "card_cvv": "str",
        "card_expiry_month": 1,
        "card_expiry_year": 1800,
        "currency": "str",
        "amount": 1
    }


@pytest.fixture(name="mock_receipt")
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

@pytest.fixture(name="test_receipt")
def create_test_receipt(mock_receipt, receipt_repo):
    receipt = receipt_repo.create(mock_receipt)
    receipt_repo.commit()
    
    return receipt

@pytest.fixture(name="idempotency_header")
def idempotency_header() -> dict[str, str]:
    return {"X-Idempotency-Key":"28323232323"}


@pytest.fixture(name="receipt_repo")
def receipt_repository():
    return ReceiptRepository(connection=psycopg.connect(get_dsn()))
