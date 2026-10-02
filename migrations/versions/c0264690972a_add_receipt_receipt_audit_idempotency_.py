"""add receipt, receipt-audit, idempotency, idempotency-audit tables

Revision ID: c0264690972a
Revises: 
Create Date: 2026-09-13 20:43:53.611577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c0264690972a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TYPE payment_states as ENUM ('pending','authorized', 'captured', 'voided', 'refunded');
        
        CREATE TABLE receipts (
            id                  SERIAL PRIMARY KEY,                                                        
            order_id            UUID                                                           NOT NULL,
            customer_id         INT                                                            NOT NULL,
            amount_in_cents     INT                                                            NOT NULL,
            currency            VARCHAR(3)                                                     NOT NULL,
            card_number         VARCHAR(100)                                                   NOT NULL,
            card_cvv            VARCHAR(3)                                                     NOT NULL,
            card_expiry_month   INT CHECK (card_expiry_month >= 1 AND card_expiry_month <= 12) NOT NULL,
            card_expiry_year    INT CHECK (card_expiry_year >= 1)                              NOT NULL,
            current_state       payment_states DEFAULT 'pending'                               NOT NULL,
            authorize_id        VARCHAR(100),
            authorized_at       TIMESTAMP,
            auth_expiry         TIMESTAMP,
            capture_id          VARCHAR(100),
            captured_at         TIMESTAMP,
            void_id             VARCHAR(100),
            voided_at           TIMESTAMP,
            refund_id           VARCHAR(100),
            refunded_at         TIMESTAMP,
            created_at          TIMESTAMP DEFAULT current_timestamp                            NOT NULL
        );  
        CREATE INDEX receipts_order_id_idx ON receipts (order_id);
        CREATE INDEX receipts_customer_id_idx ON receipts (customer_id);
        
       -- idempotency table 
        CREATE TABLE idempotency_keys 
        (
            id                  SERIAL PRIMARY KEY,
            idempotency_key     VARCHAR(100)                                        NOT NULL,
            request_path        VARCHAR(100)                                        NOT NULL,
            request_body        JSONB                                               NOT NULL,
            response_body       JSONB,
            response_code       INTEGER,
            created_at          TIMESTAMP DEFAULT current_timestamp                 NOT NULL
        );
        
        -- allows two different receipts to use the same idempotency key
        CREATE UNIQUE INDEX idempotency_key_request_path_idx
        ON idempotency_keys (idempotency_key, request_path);
        
        -- receipt audit table
        CREATE TABLE receipts_audit
        (   
            receipt_id          INTEGER                                                        NOT NULL, 
            order_id            UUID                                                           NOT NULL,
            customer_id         INT                                                            NOT NULL,
            amount_in_cents     INT                                                            NOT NULL,
            currency            VARCHAR(3)                                                     NOT NULL,
            card_number         VARCHAR(100)                                                   NOT NULL,
            card_cvv            VARCHAR(3)                                                     NOT NULL,
            card_expiry_month   INT CHECK (card_expiry_month >= 1 AND card_expiry_month <= 12) NOT NULL,
            card_expiry_year    INT CHECK (card_expiry_year >= 1)                              NOT NULL,
            current_state       payment_states DEFAULT 'pending'                               NOT NULL,
            authorize_id        VARCHAR(100),
            authorized_at       TIMESTAMP,
            capture_id          VARCHAR(100),
            captured_at         TIMESTAMP,
            void_id             VARCHAR(100),
            voided_at           TIMESTAMP,
            refund_id           VARCHAR(100),
            refunded_at         TIMESTAMP,
            -- what action was performed on the receipts database
            action              TEXT  CHECK ( action in ('del','upd','ins'))                   NOT NULL,
            created_at          TIMESTAMP DEFAULT current_timestamp                            NOT NULL
        );
        
        -- trigger for audit table 
        CREATE OR REPLACE FUNCTION audit_func() 
        RETURNS TRIGGER 
        AS
        $body$
            BEGIN
                -- add a new row into the audit table with its corresponding action each time
                -- update, delete, insert operations are performed on the receipt table
                if (tg_op = 'UPDATE') then
                    insert into receipts_audit SELECT 
                        NEW.*, 'upd';
                    RETURN NEW;
                        
                elseif (tg_op = 'INSERT') then
                    insert into receipts_audit SELECT
                        NEW.*, 'ins';
                    RETURN NEW;
                        
                elseif (tg_op = 'DELETE') then
                    INSERT INTO receipts_audit SELECT 
                        OLD.*, 'del';
                    RETURN OLD;
                end if;      
                END;
        $body$ LANGUAGE plpgsql;
            
        CREATE TRIGGER receipt_audit
        -- after because we want to audit after the operation has been fully performed
        AFTER INSERT OR UPDATE OR DELETE ON receipts
        FOR EACH ROW EXECUTE PROCEDURE audit_func()
            """
        )

def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP TABLE receipts CASCADE;
        DROP TABLE idempotency_keys;
        DROP TABLE receipts_audit;
            
        DROP TYPE payment_states; 
        """
    )
