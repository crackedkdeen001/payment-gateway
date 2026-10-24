from psycopg import Connection, sql
from pydantic import BaseModel


class GenericRepository:
    class_row = None
    
    def __init__(self, connection: Connection):
        self._conn = connection
        self.columns = None
        self.table_name = None
        self.class_row = type(self).class_row
        
    def update(self, model, **params) -> BaseModel | None:
        with self._conn.cursor(row_factory=self.class_row) as cursor:
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
            
            updated_key = cursor.execute(query, values)
            return updated_key.fetchone()

    def commit(self):
         self._conn.commit()
