import psycopg
import pytest

from dtos import helpers
from src.models import PaymentStates, Receipt
from src.db import get_dsn
from src.repository import ReceiptRepository    

def test_create_a_receipt_record(test_database, mock_receipt: Receipt, receipt_repo):
    receipt = receipt_repo.create(mock_receipt)
    receipt_repo.commit()
    
    assert receipt is not None
    assert receipt.amount_in_cents == 2929

def test_updating_a_receipt_record(test_database, test_receipt: Receipt, receipt_repo):
    actual_receipt = receipt_repo.update(model=test_receipt, current_state=PaymentStates.REFUNDED)
    
    assert actual_receipt is not None
    assert actual_receipt.current_state == PaymentStates.REFUNDED

def test_get_a_receipt_record_by_id(test_database, test_receipt: Receipt, receipt_repo):
    receipt = receipt_repo.create(test_receipt)
    actual_receipt = receipt_repo.get_by_id(receipt_id=receipt.id)
    
    assert actual_receipt is not None
    assert actual_receipt.id == 1


def test_get_a_receipt_record_by_customer_id(test_database, test_receipt: Receipt, receipt_repo):
    actual_receipt = receipt_repo.get_by_customer_id(customer_id=test_receipt.customer_id)

    assert actual_receipt is not None
    assert helpers.CustomerID == 1
    
def test_get_a_receipt_record_by_order_id(test_database, test_receipt: Receipt, receipt_repo):
    actual_receipt = receipt_repo.get_by_order_id(order_id=test_receipt.order_id)

    assert actual_receipt is not None
    assert helpers.OrderID == test_receipt.order_id # uuid is random on each test
