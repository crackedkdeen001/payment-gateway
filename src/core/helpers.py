from psycopg.types.json import Jsonb


def toJsonb(python_dict: dict | None):
    if python_dict is None:
        return
    return Jsonb(python_dict)

