from datetime import datetime

import psycopg
import pytest
from psycopg.types.json import Jsonb

from src.models.states import PaymentStates


# Database is created on every test
class TestReceipt:
    def test_create_one_receipt_row_with_default_state(self, receipt_cur):
        query = """
        INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year)
        VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 9, 323320, 'USD', '121239', '360', 8, 2001)
        RETURNING *;
        """ 
        receipt = receipt_cur.execute(query).fetchone()
        
        assert receipt is not None
        assert receipt.current_state == PaymentStates.PENDING

    def test_create_multiple_receipt_rows_with_non_default_states(self, receipt_cur):
        query = """
        INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state) 
        VALUES
        ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 9, 323320, 'USD', '121239', '360', 8, 2001, 'authorized'),
        ('ec7dfc0d-3a12-482d-abff-9860e2cb36a4'::uuid, 6, 2326, 'USD', '60121233', '358', 12, 2035, 'refunded'),
        ('89e6075c-a7cd-4cc5-9a32-7e75c2d942ab'::uuid, 5, 34343424, 'EUR', '150525', '353', 11, 2021, 'captured'),
        ('44457467-a47d-44e6-98c1-4e18c6d83828'::uuid, 4, 233354, 'NGN', '2414225', '359',6 , 2011, 'voided')
        RETURNING *;
        """
        receipts = receipt_cur.execute(query).fetchall()
            
        auth_receipt = receipts[0]
        refunded_receipt = receipts[1]
        captured_receipt = receipts[2]
        voided_receipt = receipts[3]
        
        assert receipts is not None
        assert len(receipts) == 4
        assert auth_receipt.current_state == PaymentStates.AUTHORIZED
        assert refunded_receipt.current_state == PaymentStates.REFUNDED
        assert captured_receipt.current_state == PaymentStates.CAPTURED
        assert voided_receipt.current_state == PaymentStates.VOIDED

    def test_create_invalid_receipt_row(self, receipt_cur):
        with pytest.raises(psycopg.DatabaseError):
            # add receipt with invalid payment state
            query = """
            INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state)
            VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 1, 20, 'usd', '121233', '343', 12, 2001, 'authorize');
            """
            
            receipt_cur.execute(query)
            
            
    def test_update_receipt_row(self, receipt_cur):
        insert_query = """
        INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state)
        VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 1, 20, 'usd', '121233', '343', 12, 2001, 'authorized')
        RETURNING *;
        """
        old_receipt = receipt_cur.execute(insert_query).fetchone()
        
        update_query = """ UPDATE receipts SET current_state='refunded' WHERE id = 1 RETURNING *; """
        new_receipt = receipt_cur.execute(update_query).fetchone()
        
        assert old_receipt.current_state == PaymentStates.AUTHORIZED
        assert new_receipt.current_state == PaymentStates.REFUNDED
            
        
    def test_delete_receipt_row(self, receipt_cur):
        insert_query = """
        INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state)
        VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 1, 20, 'usd', '121233', '343', 12, 2001, 'authorized')
        RETURNING *;
        """
        receipt = receipt_cur.execute(insert_query).fetchone()
        assert receipt is not None

        delete_query=""" DELETE FROM receipts WHERE id = 1;"""
        receipt_cur.execute(delete_query)

        select_query = """SELECT * FROM receipts;"""
        no_receipt = receipt_cur.execute(select_query).fetchone()
        
        # the receipt should no longer exist
        assert no_receipt is None
        
    
    def test_bank_reference_timestamp_trigger(self, receipt_cur):
        insert_query = """
        INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state)
        VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 1, 20, 'usd', '121233', '343', 12, 2001, 'authorized'),
        ('f726ad17-2928-40e2-8ce8-16cda358bc15'::uuid, 1, 20, 'usd', '121233', '343', 12, 2001, 'captured'),
        ('17aeea5d-54ca-48d9-b9a5-4e29dc35cb33'::uuid, 1, 20, 'usd', '121233', '343', 12, 2001, 'refunded'),
        ('39635382-a7c0-4b85-8c94-3a6a67196239'::uuid, 1, 20, 'usd', '121233', '343', 12, 2001, 'voided')
        RETURNING *;
        """

        receipts = receipt_cur.execute(insert_query).fetchall()
        auth_receipt = receipts[0]
        captured_receipt = receipts[1]
        refunded_receipt = receipts[2]
        voided_receipt = receipts[3]
        
        assert auth_receipt.bank_reference.authorized_at is not None     
        assert isinstance(auth_receipt.bank_reference.authorized_at, datetime)
        
        assert captured_receipt.bank_reference.captured_at is not None
        assert isinstance(captured_receipt.bank_reference.captured_at, datetime)
        
        assert refunded_receipt.bank_reference.refunded_at is not None
        assert isinstance(refunded_receipt.bank_reference.refunded_at, datetime)
        
        assert voided_receipt.bank_reference.voided_at is not None
        assert isinstance(voided_receipt.bank_reference.voided_at, datetime)
        

        
    def test_receipt_audit_trigger_on_all_actions(self, build_schema, postgresql):
        with postgresql.cursor() as cur:
            insert_query = """
            INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state)
            VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 1, 20, 'usd', '121233', '343', 12, 2001, 'authorized');
            """
            update_query = """UPDATE receipts SET current_state='refunded' WHERE id = 1;"""
            delete_query =  """ DELETE FROM receipts WHERE id = 1 """
            
            cur.execute(insert_query)
            cur.execute(update_query)
            cur.execute(delete_query)

            # receipt audit should be populated 3 times
            audit_query = """ SELECT * FROM receipts_audit;"""
            audit = cur.execute(audit_query).fetchall()
            
            insert_audit = audit[0]
            update_audit = audit[1]
            delete_audit = audit[2]

            assert audit is not None
            assert len(audit) == 3
            assert insert_audit[19] == "ins"
            assert update_audit[19] == "upd"
            assert delete_audit[19] == "del"

            
    def test_card_month_constraint(self, receipt_cur):
        with pytest.raises(psycopg.IntegrityError):
            # set card year to 13 
            # month must be within 1 and 12
            query = """
            INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state)
            VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 1, 20, 'usd', '121233', '343', 13, 2001, 'authorized')
            """
            receipt_cur.execute(query)
            
    def test_card_card_year_constraint(self, receipt_cur):
        with pytest.raises(psycopg.IntegrityError):
            # card year cannot be less than 0
            query = """
            INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state)
            VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 1, 20, 'usd', '121233', '343', 12, -1, 'authorized');
            """
            receipt_cur.execute(query)
    
    def test_character_limits_on_columns_with_varchar_type(self, receipt_cur):
        with pytest.raises(psycopg.DatabaseError):
            # the currency has a character limit of 3
            # and we used 5 characters
            query =  """
            INSERT INTO receipts (order_id, customer_id, amount_in_cents, currency, card_number, card_cvv, card_expiry_month, card_expiry_year, current_state)
            VALUES ('ef51aa3f-620c-4783-8701-8e37a225538e'::uuid, 1, 20, 'usd22', '121233', '343', 13, 2001, 'authorized');
            """
            receipt_cur.execute(query)
            
            
# not many tests are needed for idempotency keys table 
# as it is only going to be written to and read from but never updated

class TestIdempotency:
    req_params = [Jsonb({"auth_code": 128182812})]

    def test_create_idempotency_row(self,receipt, idem_cur):
        insert_query = """
        INSERT INTO idempotency_keys (idempotency_key, request_path, request_params, response_body, response_code, receipt_id) 
        VALUES ('678923232323', '/api/v3/google', (%s), NULL, NULL, 1) 
        RETURNING *;
        """
        
        idempotency_row = idem_cur.execute(insert_query, TestIdempotency.req_params).fetchone()
        
        assert idempotency_row is not None
        assert idempotency_row.receipt_id == 1
        assert idempotency_row.idempotency_key == "678923232323"
        
        
    def test_not_null_constraint(self, receipt, idem_cur):
        with pytest.raises(psycopg.IntegrityError):
            insert_query = """
            INSERT INTO idempotency_keys (idempotency_key, request_path, request_params, response_body, response_code, receipt_id)
            VALUES ('678923232323', NULL , (%s), NULL, NULL, 1)
            RETURNING *; 
            """
            idem_cur.execute(insert_query, TestIdempotency.req_params)