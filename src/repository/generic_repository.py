from psycopg import Connection, sql
from pydantic import BaseModel


class GenericRepository:
    def __init__(self, connection: Connection):
        self._conn = connection
        self.columns = None
        self.table_name = None
        
    def update(self, model, **params) -> BaseModel | None:
        with self._conn.cursor() as cursor:
            values = []
            set_clause = []

            # get valid fields for updating
            for field, value in params.items():
                if field in self.columns:
                    values.append(value)

                # build the  statement dynamically
                set_clause.append(
                    sql.SQL("{} = {}").format(
                        sql.Identifier(field),
                        sql.Placeholder()
                    )
                )

            # interpolate the values into the query
            query = sql.SQL(
                """
                UPDATE {}
                SET {}
                WHERE id = {}
                RETURNING *;
                """
            ).format(sql.Identifier(self.table_name),
            sql.SQL(", ").join(set_clause),
            sql.Literal(model.id)
            )

            updated_key = cursor.execute(query, values).fetchone()
            self._conn.commit()
            
            return updated_key
