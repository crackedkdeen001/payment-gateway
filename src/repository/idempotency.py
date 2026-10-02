from psycopg.rows import class_row

from src.models import IdempotencyKey
from src.core import toJsonb
from psycopg import Connection, sql
from src.db.setup import Conn

"""
methods

create an idempotent record
get a cached record using the idempotency key
"""

class IdempotencyRepository:
    def __init__(self, connection: Connection):
        self._conn = connection
        self._conn.row_factory = class_row(IdempotencyKey)
        self.columns = IdempotencyKey.model_fields.keys()
        

    def create(self, record: IdempotencyKey):
        with self._conn.cursor() as cursor:
            params = record.model_dump()
            
            # delete useless parameters
            del params["id"]
            del params["created_at"]
            
            params["request_body"] = toJsonb(params["request_body"])
            params["response_body"] = toJsonb(params["response_body"])

            row = cursor.execute(
            """
            INSERT INTO idempotency_keys (idempotency_key, request_path, request_body, response_body, response_code)
            VALUES (%(idempotency_key)s, %(request_path)s, %(request_body)s, %(response_body)s, %(response_code)s)
            RETURNING *;
            """, 
            params=params
            )
            self._conn.commit()

    def get(self, idempotency_key: str, request_path) -> IdempotencyKey | None:
        with self._conn.cursor() as cursor:
            row = cursor.execute(
            """
            SELECT * FROM idempotency_keys 
            WHERE idempotency_key = %s AND request_path = %s;
            """,
            params=(idempotency_key, request_path))
            
            self._conn.commit()
            return row.fetchone()
        
    def update(self,key: IdempotencyKey, **params):
        with self._conn.cursor() as cursor:
            values = []
            set_clause = []
            
            # get valid fields for updating
            for field, value in params.items():
                if field in self.columns:
                    values.append(value)
                
                # build the SET statement dynamically
                set_clause.append(
                    sql.SQL("{} = {}").format(
                        sql.Identifier(field),
                        sql.Placeholder()
                    )
                )
                
                # interpolate the values
                query = sql.SQL(
                    """
                    UPDATE idempotency_keys
                    SET {}
                    WHERE id = {}
                    RETURNING *;
                    """
                ).format(
                    sql.SQL(", ").join(set_clause),
                    sql.Literal(key.id)
                )
                
                updated_key = cursor.execute(query, values).fetchone()
                self._conn.commit()
                return updated_key
               
                    
            
        