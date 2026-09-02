from typing import Annotated

from sqlalchemy.orm import Session

from db.setup import app_session


def get_session():
    with app_session() as session:
        yield session


SessionDep = Annotated[Session, get_session]
