import psycopg
from psycopg import Connection, sql
from pydantic import BaseModel


class GenericRepository:
    class_row = None
    
    def __init__(self, connection: psycopg.AsyncConnection):
        self._conn = connection
        self.columns = None
        self.table_name = None
        self.class_row = type(self).class_row
        
    async def update(self, model, **params) -> BaseModel | None:
       async with self._conn.cursor(row_factory=self.class_row) as cursor:
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
            
            updated_key = await cursor.execute(query, values)
            return await updated_key.fetchone()

    async def commit(self):
         await self._conn.commit()
