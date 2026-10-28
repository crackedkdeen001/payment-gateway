from uuid import UUID

from psycopg import Connection, sql
from psycopg.rows import class_row

from src.models import Receipt
from src.repository.generic_repository import GenericRepository

class ReceiptRepository(GenericRepository):
    class_row = class_row(Receipt)

    def __init__(self, connection: Connection):
        super().__init__(connection)
        self.columns = Receipt.model_fields.keys()
        self.table_name = "receipts"
        
    # create a receipt in the database
    def create(self, receipt: Receipt):
        with self._conn.cursor(row_factory=self.class_row) as  cursor:
            fields = receipt.model_dump(exclude={"id", "created_at"})
            query = """
            INSERT INTO receipts 
            (order_id, customer_id, amount_in_cents, currency,
             card_number, card_cvv, card_expiry_month, card_expiry_year,
             current_state, authorize_id, authorized_at, auth_expiry,
             capture_id, captured_at, void_id, voided_at, refund_id, refunded_at) 
            VALUES  (%(order_id)s, %(customer_id)s, %(amount_in_cents)s, %(currency)s,
                    %(card_number)s,%(card_cvv)s, %(card_expiry_month)s, %(card_expiry_year)s,
                    %(current_state)s, %(authorize_id)s, %(authorized_at)s, %(auth_expiry)s,
                    %(capture_id)s, %(captured_at)s, %(void_id)s, %(voided_at)s,
                    %(refund_id)s, %(refunded_at)s)
            ON CONFLICT(order_id) DO NOTHING
            RETURNING *;
            """ 
            receipt = cursor.execute(query, params=fields)
            
            return receipt.fetchone()
            
    def update(self, model: Receipt, **params) -> Receipt | None:
        return super().update(model, **params)

    def create_audit(self, receipt: Receipt, action: str) -> None:
        fields = receipt.model_dump(exclude={"id", "created_at"})
        fields["receipt_id"] = receipt.id
        fields["action"] = action
        columns = ("receipt_id", "order_id", "customer_id", "amount_in_cents", "currency",
                   "card_number", "card_cvv", "card_expiry_month", "card_expiry_year",
                   "current_state", "authorize_id", "authorized_at", "capture_id", "captured_at",
                   "void_id", "voided_at", "refund_id", "refunded_at", "action")
        with self._conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO receipts_audit (" + ", ".join(columns) + ") VALUES (" +
                ", ".join("%(" + column + ")s" for column in columns) + ")",
                fields,
            )
    
    def get_by_id(self, receipt_id: int) -> Receipt | None:
        return self._get_by(field_name="id", field_value=receipt_id)
        
    def get_by_customer_id(self, customer_id: int) -> Receipt | None:
        return self._get_by(field_name="customer_id", field_value=customer_id)

    def get_by_order_id(self, order_id: UUID) -> Receipt | None:
        return self._get_by(field_name="order_id", field_value=order_id)

    def _get_by(self, field_name, field_value) -> Receipt | None:
        with self._conn.cursor(row_factory=self.class_row) as cursor:
            query = sql.SQL("SELECT * FROM receipts WHERE {0} = {1}").format(sql.Identifier(field_name), sql.Literal(field_value))
            
            receipt = cursor.execute(query).fetchone()
            return receipt
