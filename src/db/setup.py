from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.core.config import settings

engine = create_engine(settings.database_url)
app_session = sessionmaker(engine)

class Base(DeclarativeBase):
    pass
