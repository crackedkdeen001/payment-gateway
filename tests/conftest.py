from pathlib import Path

import pytest
from pytest_postgresql import factories

path_to_sql = Path.cwd().parent / Path("src/db/schema/schema.sql")

# Make the test database be populated with the schema per test session run.
test_postgresql_proc = factories.postgresql_proc(
    load=[path_to_sql]
)

test_postgresql = factories.postgresql("test_postgresql_proc")

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

@pytest.fixture(name="idempotency_header")
def idempotency_header() -> dict[str, str]:
    return {"X-Idempotency-Key":"28323232323"}
