from uuid import uuid4

import psycopg
import pytest

from src.models import PaymentStates
from src.db import get_conn_string
from src.repository import ReceiptRepository
from src.models import Receipt

@pytest.fixture(name="receipt_repo")
def receipt_repository():
    return  ReceiptRepository(connection=psycopg.connect(get_conn_string()))

@pytest.fixture(name="demo_receipt")
def create_demo_receipt(receipt_repo, receipt):
    receipt_repo.create(receipt)
    

def test_create_a_receipt_record(test_postgresql, receipt, receipt_repo):
    receipt_repo.create(receipt)


def test_updating_a_receipt_record(test_postgresql, receipt, receipt_repo, demo_receipt):
    test_receipt = receipt_repo.update(receipt, current_state=PaymentStates.CAPTURED)
    
    assert test_receipt is not None
    assert test_receipt.current_state == PaymentStates.CAPTURED

def test_get_a_receipt_record_by_id(test_postgresql, receipt, receipt_repo):
    test_receipt = receipt_repo.get_by_id(receipt_id=1)
    
    assert test_receipt is not None
    assert test_receipt.id == 1


def test_get_a_receipt_record_by_customer_id(test_postgresql, receipt, receipt_repo):
    test_receipt = receipt_repo.get_by_customer_id(customer_id=1)

    assert test_receipt is None

def test_get_a_receipt_record_by_order_id(test_postgresql, receipt, receipt_repo):
    test_receipt = receipt_repo.get_by_order_id(order_id=uuid4())

    assert test_receipt is None
