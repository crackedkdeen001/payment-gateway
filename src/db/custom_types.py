from typing import Any

from sqlalchemy import Dialect, types
from sqlalchemy.sql.type_api import _T


class MyRefID(types.TypeDecorator):
    """
    Adds my prefix for the receipt id column in the database.
    The prefix is removed when the ID is persisted and added
    when the ref_id is pulled from the database
    """

    impl = types.Integer

    def process_bind_param(self, value: _T | None, dialect: Dialect) -> Any:
        return "kdeen2099__" + str(value)

    def process_result_value(
            self, value: Any | None, dialect: Dialect
    ) -> _T | None:
        return int(value[9:])
