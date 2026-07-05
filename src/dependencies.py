from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from src.database.database import engine


def get_db():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
