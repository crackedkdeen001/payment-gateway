from psycopg.rows import class_row

from src.repository.generic_repository import GenericRepository
from src.models import IdempotencyKey
from src.repository.helpers import toJson
from psycopg import Connection


class IdempotencyRepository(GenericRepository):
    class_row = class_row(IdempotencyKey)
    
    def __init__(self, connection: Connection):
        super().__init__(connection)
        self.columns = IdempotencyKey.model_fields.keys()
        self.table_name = "idempotency_keys"
        

    def create(self, idempotency_record: IdempotencyKey):
        with self._conn.cursor(row_factory=self.class_row) as cursor:
            fields = idempotency_record.model_dump(exclude={"id", "created_at"})
            
            # delete fields that are made at db level
            fields["request_body"] = toJson(fields["request_body"])
            fields["response_body"] = toJson(fields["response_body"])

            row = cursor.execute(
            """
            INSERT INTO idempotency_keys (idempotency_key, request_path, request_body, response_body, response_code)
            VALUES (%(idempotency_key)s, %(request_path)s, %(request_body)s, %(response_body)s, %(response_code)s)
            RETURNING *;
            """, 
            params=fields
            )
            # self._conn.commit()
            return row.fetchone()

    def get(self, idempotency_key: str, request_path) -> IdempotencyKey | None:
        with self._conn.cursor(row_factory=self.class_row) as cursor:
            row = cursor.execute(
            """
            SELECT * FROM idempotency_keys 
            WHERE idempotency_key = %s AND request_path = %s;
            """,
            params=(idempotency_key, request_path))

            # self._conn.commit()
            return row.fetchone()
        
    def update(self, model: IdempotencyKey, **params)-> IdempotencyKey | None:
        super().update(model, **params)
