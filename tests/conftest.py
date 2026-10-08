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
def card_data():
    return  {
    "number": "23923",
    "cvv": "231",
    "expiry_month": 12,
    "expiry_year":2028
}
