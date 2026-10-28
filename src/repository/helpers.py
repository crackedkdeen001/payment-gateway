from psycopg.types.json import Json


def toJson(python_dict: dict | None):
    if python_dict is None:
        return
    return Json(python_dict)

